package com.openregex.models;

import com.fasterxml.jackson.annotation.JsonInclude;
import java.util.List;

public class Models {
    public record MatchRequest(String task_id, String engine_id, String regex, String text, List<String> flags) {}

    @JsonInclude(JsonInclude.Include.NON_NULL)
    public record MatchGroup(int group_id, String name, String content, int start, int end) {}

    public record MatchItem(int match_id, String full_match, int start, int end, List<MatchGroup> groups) {}

    @JsonInclude(JsonInclude.Include.NON_NULL)
    public record MatchResult(String task_id, String engine_id, boolean success, List<MatchItem> matches, double execution_time_ms, String error) {}

    public record CheatSheetItem(String character, String description) {}

    public record CheatSheetCategory(String category, List<CheatSheetItem> items) {}

    public record EngineDocs(List<String> trivia, String cheat_sheet_url) {}

    public record EngineFlag(String name, String description, String group) {}

    public record EngineCapabilities(List<EngineFlag> flags, boolean supports_lookaround, boolean supports_backrefs) {}

    public record EngineExample(String regex, String text) {}

    public record EngineInfo(
            String engine_id,
            String engine_language_type,
            String engine_language_version,
            String engine_regex_lib,
            String engine_regex_lib_version,
            String engine_label,
            EngineCapabilities engine_capabilities,
            EngineDocs engine_docs,
            List<CheatSheetCategory> engine_cheat_sheet,
            List<EngineExample> engine_examples
    ) {}

    public record WorkerInfo(
            String worker_name,
            String worker_version,
            String worker_release_date,
            List<EngineInfo> engines
    ) {}
}
