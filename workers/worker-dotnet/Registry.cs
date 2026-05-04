using StackExchange.Redis;
using System.Text.Json;
using System.Reflection;
using System.Runtime.InteropServices;

namespace OpenRegex.Worker;

public static class Registry
{
    private static readonly Dictionary<string, (string Description, string Group)> FlagMetadata = new()
    {
        ["i"] = ("Case-insensitive matching.", "Basic"),
        ["m"] = ("Multiline mode. Makes ^ and $ work per line.", "Basic"),
        ["s"] = ("DotAll mode. Makes . match newline.", "Basic"),
        ["x"] = ("Extended/free-spacing pattern mode.", "Basic"),
        ["n"] = ("Explicit capture mode for unnamed groups.", "Advance"),
        ["r"] = ("Right-to-left matching mode.", "Unique")
    };

    private static List<EngineFlag> BuildEngineFlags(params string[] names)
    {
        var flags = new List<EngineFlag>(names.Length);
        foreach (var name in names)
        {
            (string Description, string Group) meta = FlagMetadata.TryGetValue(name, out var value)
                ? value
                : ($"Flag ({name})", "Basic");
            flags.Add(new EngineFlag(name, meta.Description, meta.Group));
        }
        return flags;
    }

    public static async Task RegisterEnginesAsync(IDatabase db)
    {
        var workerVersion = Environment.GetEnvironmentVariable("WORKER_VERSION") ?? "Unknow";
        var libVersion = RuntimeInformation.FrameworkDescription;
        var releaseDate = Environment.GetEnvironmentVariable("WORKER__RELEASE_DATE") ?? "Unreleased";
        var langVersion = $"{Environment.Version.Major}.{Environment.Version.Minor}";

        var workerInfo = new WorkerInfo(
            WorkerName: "worker-dotnet",
            WorkerVersion: workerVersion,
            WorkerReleaseDate: releaseDate,
            Engines: new List<EngineInfo>
            {
                new EngineInfo(
                    EngineId: $"dotnet{langVersion}_standard",
                    EngineLanguageType: "C#",
                    EngineLanguageVersion: langVersion,
                    EngineRegexLib: "System.Text.RegularExpressions",
                    EngineRegexLibVersion: libVersion,
                    EngineLabel: "C# (.NET)",
                    EngineCapabilities: new EngineCapabilities(
                        Flags: BuildEngineFlags("i", "m", "s", "x", "n", "r"),
                        SupportsLookaround: true,
                        SupportsBackrefs: true
                    ),
                    EngineDocs: new EngineDocs(
                        Trivia: new List<string>
                        {
                            "Native System.Text.RegularExpressions engine.",
                            ".NET runtime libraries (including regex) are distributed under the MIT license.",
                            "Supports Balancing Groups (e.g., '(?<depth>-...)') which allow matching balanced constructs like nested parentheses without recursion.",
                            "Supports Right-to-Left matching using the RegexOptions.RightToLeft option.",
                            "Safeguarded against ReDoS via a strict execution timeout constructor."
                        },
                        CheatSheetUrl: "https://learn.microsoft.com/en-us/dotnet/standard/base-types/regular-expression-language-quick-reference"
                    ),
                    EngineCheatSheet: new List<CheatSheetCategory>
                    {
                        new CheatSheetCategory(
                            Category: "Character Classes & Escapes",
                            Items: new List<CheatSheetItem>
                            {
                                new CheatSheetItem(".", "Any character (except newline unless 's' flag is set)"),
                                new CheatSheetItem("\\w", "Word character (alphanumeric + underscore)"),
                                new CheatSheetItem("\\W", "Non-word character"),
                                new CheatSheetItem("\\d", "Decimal digit"),
                                new CheatSheetItem("\\D", "Non-digit"),
                                new CheatSheetItem("\\s", "Whitespace character (space, tab, newline)"),
                                new CheatSheetItem("\\S", "Non-whitespace character"),
                                new CheatSheetItem("[a-z]", "Character class (inclusive)"),
                                new CheatSheetItem("[^a-z]", "Negated character class (exclusive)")
                            }
                        ),
                        new CheatSheetCategory(
                            Category: "Anchors & Boundaries",
                            Items: new List<CheatSheetItem>
                            {
                                new CheatSheetItem("^", "Start of string (or line if 'm' flag is set)"),
                                new CheatSheetItem("$", "End of string (or line if 'm' flag is set)"),
                                new CheatSheetItem("\\A", "Absolute start of string (ignores 'm' flag)"),
                                new CheatSheetItem("\\z", "Absolute end of string (ignores 'm' flag)"),
                                new CheatSheetItem("\\Z", "End of string or before final newline (ignores 'm' flag)"),
                                new CheatSheetItem("\\b", "Word boundary"),
                                new CheatSheetItem("\\B", "Non-word boundary"),
                                new CheatSheetItem("\\G", "End of the previous match")
                            }
                        ),
                        new CheatSheetCategory(
                            Category: "Quantifiers",
                            Items: new List<CheatSheetItem>
                            {
                                new CheatSheetItem("*", "0 or more times (greedy)"),
                                new CheatSheetItem("+", "1 or more times (greedy)"),
                                new CheatSheetItem("?", "0 or 1 time (greedy)"),
                                new CheatSheetItem("{m}", "Exactly m times"),
                                new CheatSheetItem("{m,n}", "Between m and n times (greedy)"),
                                new CheatSheetItem("*?", "0 or more times (lazy)"),
                                new CheatSheetItem("+?", "1 or more times (lazy)"),
                                new CheatSheetItem("??", "0 or 1 time (lazy)"),
                                new CheatSheetItem("{m,n}?", "Between m and n times (lazy)")
                            }
                        ),
                        new CheatSheetCategory(
                            Category: "Grouping & Backreferences",
                            Items: new List<CheatSheetItem>
                            {
                                new CheatSheetItem("(...)", "Capturing group"),
                                new CheatSheetItem("(?:...)", "Non-capturing group"),
                                new CheatSheetItem("x|y", "Alternation (match x or y)"),
                                new CheatSheetItem("(?<name>...)", "Named capturing group"),
                                new CheatSheetItem("\\1", "Backreference to capture group 1"),
                                new CheatSheetItem("\\k<name>", "Backreference to a named capture group")
                            }
                        ),
                        new CheatSheetCategory(
                            Category: "Lookarounds & Advanced",
                            Items: new List<CheatSheetItem>
                            {
                                new CheatSheetItem("(?=...)", "Positive lookahead"),
                                new CheatSheetItem("(?!...)", "Negative lookahead"),
                                new CheatSheetItem("(?<=...)", "Positive lookbehind (Variable-length supported!)"),
                                new CheatSheetItem("(?<!...)", "Negative lookbehind (Variable-length supported!)"),
                                new CheatSheetItem("(?>...)", "Atomic grouping (prevents backtracking inside the group)"),
                                new CheatSheetItem("(?i)", "Inline flag: Case-insensitive"),
                                new CheatSheetItem("(?m)", "Inline flag: Multiline"),
                                new CheatSheetItem("(?<name1-name2>)", "Balancing group (Pops name2 capture from stack)")
                            }
                        )
                    },
                    EngineExamples: new List<EngineExample>
                    {
                        new EngineExample(
                            Regex: @"(?<IP>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d))(/(\d{1,2}))?(?:-(?<IP2>(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)))?(:(?<port>\d{1,5}))?",
                            Text: "This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255\n192.168.1.1-192.168.1.255:80\n192.168.1.0/24:80"
                        )
                    }
                )
            }
        );

        var json = JsonSerializer.Serialize(workerInfo);
        await db.HashSetAsync("openregex:workers", workerInfo.WorkerName, json);
        Console.WriteLine($"[Worker] Registered '{workerInfo.WorkerName}' with {workerInfo.Engines.Count} engines.");
    }
}
