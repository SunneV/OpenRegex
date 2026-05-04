using System.Text.Json.Serialization;

namespace OpenRegex.Worker;

public record MatchRequest(
    [property: JsonPropertyName("task_id")] string TaskId,
    [property: JsonPropertyName("engine_id")] string EngineId,
    [property: JsonPropertyName("regex")] string Regex,
    [property: JsonPropertyName("text")] string Text,
    [property: JsonPropertyName("flags")] List<string> Flags
);

public record MatchGroup(
    [property: JsonPropertyName("group_id")] int GroupId,
    [property: JsonPropertyName("name")] string? Name,
    [property: JsonPropertyName("content")] string Content,
    [property: JsonPropertyName("start")] int Start,
    [property: JsonPropertyName("end")] int End
);

public record MatchItem(
    [property: JsonPropertyName("match_id")] int MatchId,
    [property: JsonPropertyName("full_match")] string FullMatch,
    [property: JsonPropertyName("start")] int Start,
    [property: JsonPropertyName("end")] int End,
    [property: JsonPropertyName("groups")] List<MatchGroup> Groups
);

public record MatchResult(
    [property: JsonPropertyName("task_id")] string TaskId,
    [property: JsonPropertyName("engine_id")] string EngineId,
    [property: JsonPropertyName("success")] bool Success,
    [property: JsonPropertyName("matches")] List<MatchItem> Matches,
    [property: JsonPropertyName("execution_time_ms")] double ExecutionTimeMs,
    [property: JsonPropertyName("error")] string? Error
);

public record CheatSheetItem(
    [property: JsonPropertyName("character")] string Character,
    [property: JsonPropertyName("description")] string Description
);

public record CheatSheetCategory(
    [property: JsonPropertyName("category")] string Category,
    [property: JsonPropertyName("items")] List<CheatSheetItem> Items
);

public record EngineDocs(
    [property: JsonPropertyName("trivia")] List<string> Trivia,
    [property: JsonPropertyName("cheat_sheet_url")] string CheatSheetUrl
);

public record EngineFlag(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("description")] string Description,
    [property: JsonPropertyName("group")] string Group
);

public record EngineCapabilities(
    [property: JsonPropertyName("flags")] List<EngineFlag> Flags,
    [property: JsonPropertyName("supports_lookaround")] bool SupportsLookaround,
    [property: JsonPropertyName("supports_backrefs")] bool SupportsBackrefs
);

public record EngineExample(
    [property: JsonPropertyName("regex")] string Regex,
    [property: JsonPropertyName("text")] string Text
);

public record EngineInfo(
    [property: JsonPropertyName("engine_id")] string EngineId,
    [property: JsonPropertyName("engine_language_type")] string EngineLanguageType,
    [property: JsonPropertyName("engine_language_version")] string EngineLanguageVersion,
    [property: JsonPropertyName("engine_regex_lib")] string EngineRegexLib,
    [property: JsonPropertyName("engine_regex_lib_version")] string EngineRegexLibVersion,
    [property: JsonPropertyName("engine_label")] string EngineLabel,
    [property: JsonPropertyName("engine_capabilities")] EngineCapabilities EngineCapabilities,
    [property: JsonPropertyName("engine_docs")] EngineDocs EngineDocs,
    [property: JsonPropertyName("engine_cheat_sheet")] List<CheatSheetCategory> EngineCheatSheet,
    [property: JsonPropertyName("engine_examples")] List<EngineExample> EngineExamples
);

public record WorkerInfo(
    [property: JsonPropertyName("worker_name")] string WorkerName,
    [property: JsonPropertyName("worker_version")] string WorkerVersion,
    [property: JsonPropertyName("worker_release_date")] string WorkerReleaseDate,
    [property: JsonPropertyName("engines")] List<EngineInfo> Engines
);
