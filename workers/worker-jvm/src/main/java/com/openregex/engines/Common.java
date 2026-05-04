package com.openregex.engines;

import com.openregex.models.Models.EngineFlag;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

public class Common {
    public static final String WORKER_VERSION = System.getenv("WORKER_VERSION") != null ? System.getenv("WORKER_VERSION") : "Unknown";
    public static final String WORKER_RELEASE_DATE = System.getenv("WORKER_RELEASE_DATE") != null ? System.getenv("WORKER_RELEASE_DATE") : "Unreleased";
    public static final String JAVA_VERSION = System.getProperty("java.version");

    public static final String CAT_CLASSES = "Character Classes & Escapes";
    public static final String CAT_ANCHORS = "Anchors & Boundaries";
    public static final String CAT_QUANTIFIERS = "Quantifiers";
    public static final String CAT_GROUPS = "Grouping & Backreferences";
    public static final String CAT_ADVANCED = "Lookarounds & Advanced";

    private record FlagMeta(String description, String group) {}

    private static final Map<String, FlagMeta> FLAG_METADATA = Map.ofEntries(
            Map.entry("i", new FlagMeta("Case-insensitive matching.", "Basic")),
            Map.entry("m", new FlagMeta("Multiline mode. Makes ^ and $ work per line.", "Basic")),
            Map.entry("s", new FlagMeta("DotAll mode. Makes . match newline.", "Basic")),
            Map.entry("d", new FlagMeta("Unix lines mode for Java Pattern anchors and dot behavior.", "Advance")),
            Map.entry("u", new FlagMeta("Unicode-aware case folding mode.", "Basic")),
            Map.entry("x", new FlagMeta("Comments/free-spacing mode.", "Basic")),
            Map.entry("U", new FlagMeta("Unicode character classes in Java; ungreedy mode in RE2J.", "Advance"))
    );

    public static List<EngineFlag> flags(String... names) {
        return Arrays.stream(names)
                .map(name -> {
                    FlagMeta meta = FLAG_METADATA.getOrDefault(name, new FlagMeta("Flag (" + name + ")", "Basic"));
                    return new EngineFlag(name, meta.description(), meta.group());
                })
                .toList();
    }
}
