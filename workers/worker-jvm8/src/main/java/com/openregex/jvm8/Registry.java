package com.openregex.jvm8;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import redis.clients.jedis.Jedis;

/**
 * Builds the engine descriptor for the legacy JDK worker.
 *
 * <p>Everything here is written against Java 8 on purpose: no records, no
 * List.of, no var. The whole point of this worker is to run java.util.regex as
 * it behaves on the JDK that most enterprise code is still pinned to, so the
 * source has to compile for that release too.</p>
 */
public final class Registry {

    public static final String WORKER_NAME = "worker-jvm8";
    public static final String ENGINE_ID = "java8_standard";

    // Contract version: "1.1" = match offsets normalized to Unicode code points.
    public static final String WORKER_SCHEMA_VERSION = "1.1";

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private Registry() {
    }

    private static String env(String key, String fallback) {
        String value = System.getenv(key);
        return (value == null || value.isEmpty()) ? fallback : value;
    }

    private static ObjectNode flag(String name, String description, String group) {
        ObjectNode node = MAPPER.createObjectNode();
        node.put("name", name);
        node.put("description", description);
        node.put("group", group);
        return node;
    }

    private static ObjectNode item(String character, String description) {
        ObjectNode node = MAPPER.createObjectNode();
        node.put("character", character);
        node.put("description", description);
        return node;
    }

    private static ObjectNode category(String name, ObjectNode... items) {
        ObjectNode node = MAPPER.createObjectNode();
        node.put("category", name);
        ArrayNode array = node.putArray("items");
        for (ObjectNode current : items) {
            array.add(current);
        }
        return node;
    }

    private static ObjectNode buildEngine() {
        String javaVersion = System.getProperty("java.version");

        ObjectNode engine = MAPPER.createObjectNode();
        engine.put("engine_id", ENGINE_ID);
        engine.put("engine_language_type", "Java");
        engine.put("engine_language_version", javaVersion);
        engine.put("engine_regex_lib", "java.util.regex");
        engine.put("engine_regex_lib_version", javaVersion);
        engine.put("engine_label", "Java 8 (java.util.regex)");

        ObjectNode capabilities = engine.putObject("engine_capabilities");
        ArrayNode flags = capabilities.putArray("flags");
        flags.add(flag("i", "Case-insensitive matching.", "Basic"));
        flags.add(flag("m", "Multiline mode. Makes ^ and $ work per line.", "Basic"));
        flags.add(flag("s", "DotAll mode. Makes . match newline.", "Basic"));
        flags.add(flag("d", "Unix lines mode: only \\n is treated as a line terminator.", "Advance"));
        flags.add(flag("u", "Unicode-aware case folding mode.", "Basic"));
        flags.add(flag("x", "Comments/free-spacing mode.", "Basic"));
        flags.add(flag("U", "Unicode character classes: \\w, \\d and \\s follow Unicode rules.", "Advance"));
        capabilities.put("supports_lookaround", true);
        capabilities.put("supports_backrefs", true);

        ObjectNode docs = engine.putObject("engine_docs");
        ArrayNode trivia = docs.putArray("trivia");
        trivia.add("Java 8 is still the most widely deployed JDK in enterprise code, and its regex engine is frozen in 2014.");
        trivia.add("In OpenJDK builds, java.util.regex is part of code distributed under GPL-2.0 with the Classpath Exception.");
        trivia.add("Compare this engine with the modern JDK worker: the syntax is nearly identical, but the behaviour of \\b, case folding and Unicode scripts has been fixed and extended several times since.");
        trivia.add("Java 9 added \\b{g} for grapheme cluster boundaries and \\X for extended grapheme clusters - write them here and Java 8 rejects the pattern.");
        trivia.add("Java 20 changed \\b to be Unicode-aware by default under UNICODE_CHARACTER_CLASS; on 8 the word-boundary definition stays ASCII unless you ask for it.");
        trivia.add("Named groups (?<name>...) exist since Java 7, but \\k<name> backreferences and Matcher.group(String) still surprise people migrating from Perl.");
        trivia.add("java.util.regex has no execution limit of any kind, so a nested quantifier will happily burn a core forever. OpenRegex wraps the subject in an interruptible CharSequence to enforce the SLA.");
        docs.put("cheat_sheet_url", "https://docs.oracle.com/javase/8/docs/api/java/util/regex/Pattern.html");

        ArrayNode cheatSheet = engine.putArray("engine_cheat_sheet");
        cheatSheet.add(category("Character Classes & Escapes",
                item(".", "Any character except a line terminator unless the 's' flag is set"),
                item("\\w", "Word character; ASCII-only unless the 'U' flag is set"),
                item("\\W", "Non-word character"),
                item("\\d", "Decimal digit; ASCII-only unless the 'U' flag is set"),
                item("\\D", "Non-digit"),
                item("\\s", "Whitespace character"),
                item("\\S", "Non-whitespace character"),
                item("\\p{Alpha}", "POSIX character class (US-ASCII only)"),
                item("\\p{L}", "Unicode general category"),
                item("\\p{IsGreek}", "Unicode script"),
                item("\\p{InGreek}", "Unicode block"),
                item("[a-z]", "Character class"),
                item("[^a-z]", "Negated character class"),
                item("[a-z&&[^bc]]", "Character class subtraction via intersection")));
        cheatSheet.add(category("Anchors & Boundaries",
                item("^", "Start of input, or start of line if the 'm' flag is set"),
                item("$", "End of input, or end of line if the 'm' flag is set"),
                item("\\A", "Start of input, always"),
                item("\\z", "End of input, always"),
                item("\\Z", "End of input, ignoring a final line terminator"),
                item("\\G", "End of the previous match"),
                item("\\b", "Word boundary; ASCII definition unless the 'U' flag is set"),
                item("\\B", "Non-word boundary")));
        cheatSheet.add(category("Quantifiers",
                item("*", "0 or more times, greedy"),
                item("+", "1 or more times, greedy"),
                item("?", "0 or 1 time, greedy"),
                item("{m,n}", "Between m and n times, greedy"),
                item("*?", "0 or more times, lazy"),
                item("+?", "1 or more times, lazy"),
                item("??", "0 or 1 time, lazy"),
                item("*+", "0 or more times, possessive"),
                item("++", "1 or more times, possessive"),
                item("?+", "0 or 1 time, possessive")));
        cheatSheet.add(category("Grouping & Backreferences",
                item("(...)", "Capturing group"),
                item("(?:...)", "Non-capturing group"),
                item("x|y", "Alternation (match x or y)"),
                item("(?<name>...)", "Named capturing group"),
                item("\\1", "Backreference to capture group 1"),
                item("\\k<name>", "Backreference to a named group")));
        cheatSheet.add(category("Lookarounds & Advanced",
                item("(?=...)", "Positive lookahead"),
                item("(?!...)", "Negative lookahead"),
                item("(?<=...)", "Positive lookbehind; must have a bounded maximum length"),
                item("(?<!...)", "Negative lookbehind"),
                item("(?>...)", "Atomic group; prevents backtracking"),
                item("(?i)", "Inline flag: case-insensitive"),
                item("(?m)", "Inline flag: multiline"),
                item("(?s)", "Inline flag: dot matches line terminators"),
                item("(?x)", "Inline flag: comments / free-spacing"),
                item("(?U)", "Inline flag: Unicode character classes"),
                item("(?i:...)", "Scoped inline flag group"),
                item("\\Q...\\E", "Quote everything in between as a literal")));

        ArrayNode examples = engine.putArray("engine_examples");
        ObjectNode example = examples.addObject();
        example.put("regex", "(?<IP>(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d))(?:/(?<mask>\\d{1,2}))?(?::(?<port>\\d{1,5}))?");
        example.put("text", "This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255");

        return engine;
    }

    public static ObjectNode buildWorkerInfo() {
        ObjectNode info = MAPPER.createObjectNode();
        info.put("worker_name", WORKER_NAME);
        info.put("worker_version", env("WORKER_VERSION", "Unknown"));
        info.put("worker_release_date", env("WORKER_RELEASE_DATE", "Unreleased"));
        info.put("worker_schema_version", WORKER_SCHEMA_VERSION);
        info.putArray("engines").add(buildEngine());
        return info;
    }

    public static void registerEngines(Jedis jedis) throws Exception {
        ObjectNode info = buildWorkerInfo();
        jedis.hset("openregex:workers", WORKER_NAME, MAPPER.writeValueAsString(info));
        System.out.println("[Worker] Registered '" + WORKER_NAME + "' with 1 engine.");
    }
}
