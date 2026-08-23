using StackExchange.Redis;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;
using System.Diagnostics;
using System.Collections.Concurrent;

namespace OpenRegex.Worker;

public static class Processor
{
    private static readonly int TIMEOUT_MS = int.TryParse(Environment.GetEnvironmentVariable("WORKER_EXECUTION_TIMEOUT_MS"), out var t) ? t : 1000;
    private static readonly int MAX_INPUT_SIZE = int.TryParse(Environment.GetEnvironmentVariable("WORKER_MAX_INPUT_SIZE"), out var i) ? i : 10485760;
    private static readonly int MAX_MATCHES = int.TryParse(Environment.GetEnvironmentVariable("WORKER_MAX_MATCHES"), out var m) ? m : 10000;
    private static readonly int MAX_GROUPS = int.TryParse(Environment.GetEnvironmentVariable("WORKER_MAX_GROUPS"), out var g) ? g : 1000;
    private static readonly int MAX_JSON_SIZE = int.TryParse(Environment.GetEnvironmentVariable("WORKER_MAX_JSON_SIZE"), out var s) ? s : 10485760;

    private static readonly ConcurrentDictionary<string, Regex> _regexCache = new();
    private static readonly ConcurrentQueue<string> _cacheKeys = new();

    // .NET regex reports UTF-16 code unit offsets; the platform contract
    // requires Unicode code point indices. Returns null when the text contains
    // no surrogates (offsets already equal code point indices).
    private static int[]? BuildUtf16ToCodePointMap(string text)
    {
        bool hasSurrogates = false;
        foreach (var c in text)
        {
            if (char.IsSurrogate(c)) { hasSurrogates = true; break; }
        }
        if (!hasSurrogates) return null;

        var map = new int[text.Length + 1];
        int cp = 0;
        int u = 0;
        while (u < text.Length)
        {
            int width = char.IsHighSurrogate(text[u]) && u + 1 < text.Length && char.IsLowSurrogate(text[u + 1]) ? 2 : 1;
            map[u] = cp;
            if (width == 2) map[u + 1] = cp;
            u += width;
            cp++;
        }
        map[text.Length] = cp;
        return map;
    }

    private static int ToCodePointIndex(int[]? map, int utf16Index)
        => map == null ? utf16Index : map[Math.Min(utf16Index, map.Length - 1)];

    private static async Task HandleDlqAsync(IDatabase db, string taskJson, string errorMessage)
    {
        try
        {
            var node = JsonNode.Parse(taskJson) as JsonObject;
            if (node != null)
            {
                int attemptCount = node.TryGetPropertyValue("attempt_count", out var ac) && ac != null ? (int)ac : 0;
                node["attempt_count"] = attemptCount + 1;
                node["error_reason"] = errorMessage;
                await db.ListLeftPushAsync("queue:dotnet:dead", node.ToJsonString());
            }
        }
        catch { /* Failsafe */ }
    }

    public static async Task ListenAndProcessAsync(IDatabase db, ISubscriber pubSub)
    {
        Console.WriteLine("[Worker] .NET worker listening on 'queue:dotnet'...");

        while (true)
        {
            try
            {
                var result = await db.ListRightPopAsync("queue:dotnet");

                if (result.IsNull)
                {
                    await Task.Delay(50);
                    continue;
                }

                _ = Task.Run(async () =>
                {
                    string taskJson = result.ToString();
                    using var jsonDoc = JsonDocument.Parse(taskJson);
                    var root = jsonDoc.RootElement;

                    var req = JsonSerializer.Deserialize<MatchRequest>(taskJson);
                    if (req == null)
                    {
                        await HandleDlqAsync(db, taskJson, "JSON Parse error");
                        return;
                    }

                    string resolvedText = req.Text;
                    string? textPayloadId = root.TryGetProperty("text_payload_id", out var tpProp) && tpProp.ValueKind == JsonValueKind.String
                        ? tpProp.GetString()
                        : null;

                    // CLAIM-CHECK: Retrieve payload if text_payload_id is present
                    if (!string.IsNullOrEmpty(textPayloadId))
                    {
                        var payload = await db.StringGetAsync(textPayloadId);
                        if (payload.IsNull)
                        {
                            await HandleDlqAsync(db, taskJson, "Payload expired or missing from Redis");
                            var errRes = new MatchResult(req.TaskId, req.EngineId, false, new List<MatchItem>(), 0.0, "Payload expired or missing from Redis");
                            var errStr = JsonSerializer.Serialize(errRes);
                            await db.StringSetAsync($"result:{req.TaskId}", errStr, TimeSpan.FromSeconds(60));
                            await pubSub.PublishAsync(RedisChannel.Literal($"result:{req.TaskId}"), "ready");
                            return;
                        }
                        resolvedText = payload.ToString();
                    }

                    var stopwatch = Stopwatch.StartNew();
                    MatchResult response;

                    try
                    {
                        if (resolvedText.Length > MAX_INPUT_SIZE)
                        {
                            throw new Exception($"Input text exceeds maximum allowed size of {MAX_INPUT_SIZE} bytes.");
                        }

                        // Engine ids end with "_nonbacktracking" for the .NET 7+
                        // automaton mode, which cannot be combined with RightToLeft.
                        bool nonBacktracking = req.EngineId.EndsWith("_nonbacktracking", StringComparison.Ordinal);

                        var options = nonBacktracking ? RegexOptions.NonBacktracking : RegexOptions.None;
                        string flagsStr = "";
                        foreach (var flag in req.Flags)
                        {
                            flagsStr += flag;
                            switch (flag)
                            {
                                case "i": options |= RegexOptions.IgnoreCase; break;
                                case "m": options |= RegexOptions.Multiline; break;
                                case "s": options |= RegexOptions.Singleline; break;
                                case "x": options |= RegexOptions.IgnorePatternWhitespace; break;
                                case "n": options |= RegexOptions.ExplicitCapture; break;
                                case "r":
                                    if (nonBacktracking)
                                    {
                                        throw new Exception("The 'r' (right-to-left) flag cannot be combined with NonBacktracking mode.");
                                    }
                                    options |= RegexOptions.RightToLeft;
                                    break;
                            }
                        }

                        string cacheKey = $"{options}|{req.Regex}";
                        if (!_regexCache.TryGetValue(cacheKey, out var regex))
                        {
                            regex = new Regex(req.Regex, options, TimeSpan.FromMilliseconds(TIMEOUT_MS));
                            _regexCache[cacheKey] = regex;
                            _cacheKeys.Enqueue(cacheKey);
                            if (_cacheKeys.Count > 1000 && _cacheKeys.TryDequeue(out var oldKey))
                            {
                                _regexCache.TryRemove(oldKey, out _);
                            }
                        }

                        var matches = regex.Matches(resolvedText);
                        var matchItems = new List<MatchItem>();
                        var cpMap = BuildUtf16ToCodePointMap(resolvedText);

                        int matchId = 0;
                        foreach (Match m in matches)
                        {
                            if (matchId >= MAX_MATCHES)
                            {
                                throw new Exception($"Exceeded maximum allowed matches ({MAX_MATCHES}).");
                            }

                            var groups = new List<MatchGroup>();
                            for (int i = 1; i < m.Groups.Count; i++)
                            {
                                if (groups.Count >= MAX_GROUPS)
                                {
                                    throw new Exception($"Exceeded maximum allowed groups per match ({MAX_GROUPS}).");
                                }

                                var g = m.Groups[i];
                                if (g.Success)
                                {
                                    string? name = regex.GroupNameFromNumber(i);
                                    if (name == i.ToString()) name = null;

                                    groups.Add(new MatchGroup(i, name, g.Value, ToCodePointIndex(cpMap, g.Index), ToCodePointIndex(cpMap, g.Index + g.Length)));
                                }
                            }
                            matchItems.Add(new MatchItem(matchId++, m.Value, ToCodePointIndex(cpMap, m.Index), ToCodePointIndex(cpMap, m.Index + m.Length), groups));
                        }

                        stopwatch.Stop();
                        response = new MatchResult(req.TaskId, req.EngineId, true, matchItems, stopwatch.Elapsed.TotalMilliseconds, null);
                    }
                    catch (RegexMatchTimeoutException)
                    {
                        stopwatch.Stop();
                        await HandleDlqAsync(db, taskJson, "TIMEOUT: .NET execution exceeded SLA.");
                        response = new MatchResult(req.TaskId, req.EngineId, false, new List<MatchItem>(), TIMEOUT_MS, $"TIMEOUT: .NET execution exceeded {TIMEOUT_MS}ms SLA.");
                    }
                    catch (Exception ex)
                    {
                        stopwatch.Stop();
                        response = new MatchResult(req.TaskId, req.EngineId, false, new List<MatchItem>(), stopwatch.Elapsed.TotalMilliseconds, ex.Message);
                    }

                    var resJson = JsonSerializer.Serialize(response);
                    if (System.Text.Encoding.UTF8.GetByteCount(resJson) > MAX_JSON_SIZE)
                    {
                        response = new MatchResult(req.TaskId, req.EngineId, false, new List<MatchItem>(), response.ExecutionTimeMs, $"Output JSON exceeds maximum allowed size of {MAX_JSON_SIZE} bytes.");
                        resJson = JsonSerializer.Serialize(response);
                    }

                    await db.StringSetAsync($"result:{req.TaskId}", resJson, TimeSpan.FromSeconds(60));
                    await pubSub.PublishAsync(RedisChannel.Literal($"result:{req.TaskId}"), "ready");
                });
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[Error] .NET Worker loop failure: {ex.Message}");
            }
        }
    }
}