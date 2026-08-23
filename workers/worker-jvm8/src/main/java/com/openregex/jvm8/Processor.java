package com.openregex.jvm8;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import redis.clients.jedis.Jedis;

import java.nio.charset.StandardCharsets;

import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Redis queue consumer running java.util.regex on a Java 8 runtime. */
public final class Processor {

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private static final String QUEUE = "queue:jvm8";
    private static final String DEAD_QUEUE = "queue:jvm8:dead";

    private static final int TIMEOUT_MS = envInt("WORKER_EXECUTION_TIMEOUT_MS", 1000);
    private static final int MAX_INPUT_SIZE = envInt("WORKER_MAX_INPUT_SIZE", 10485760);
    private static final int MAX_MATCHES = envInt("WORKER_MAX_MATCHES", 10000);
    private static final int MAX_GROUPS = envInt("WORKER_MAX_GROUPS", 1000);
    private static final int MAX_JSON_SIZE = envInt("WORKER_MAX_JSON_SIZE", 10485760);

    private static final ExecutorService EXECUTOR = Executors.newCachedThreadPool();
    private static final LRUCache<String, Pattern> CACHE = new LRUCache<String, Pattern>(1000);

    private Processor() {
    }

    private static int envInt(String key, int fallback) {
        String value = System.getenv(key);
        if (value != null && !value.isEmpty()) {
            try {
                return Integer.parseInt(value);
            } catch (NumberFormatException ignored) {
                // fall through to the default
            }
        }
        return fallback;
    }

    private static final class LRUCache<K, V> extends LinkedHashMap<K, V> {
        private final int maxEntries;

        LRUCache(int maxEntries) {
            super(maxEntries + 1, 1.0f, true);
            this.maxEntries = maxEntries;
        }

        @Override
        protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
            return size() > maxEntries;
        }
    }

    /**
     * java.util.regex has no timeout, and Matcher never checks for interruption
     * on its own. Feeding it a CharSequence that does is the only way to stop a
     * runaway pattern without killing the JVM.
     */
    private static final class InterruptibleCharSequence implements CharSequence {
        private final CharSequence inner;

        InterruptibleCharSequence(CharSequence inner) {
            this.inner = inner;
        }

        public int length() {
            return inner.length();
        }

        public char charAt(int index) {
            if (Thread.currentThread().isInterrupted()) {
                throw new RuntimeException("TIMEOUT: Java 8 execution exceeded SLA.");
            }
            return inner.charAt(index);
        }

        public CharSequence subSequence(int start, int end) {
            return new InterruptibleCharSequence(inner.subSequence(start, end));
        }

        @Override
        public String toString() {
            return inner.toString();
        }
    }

    // java.util.regex reports UTF-16 code unit offsets; the platform contract
    // requires Unicode code point indices. Returns null when the text contains
    // no surrogate pairs (offsets already equal code point indices).
    private static int[] buildUtf16ToCodePointMap(String text) {
        if (text.length() == text.codePointCount(0, text.length())) {
            return null;
        }
        int[] map = new int[text.length() + 1];
        int codePoint = 0;
        int unit = 0;
        while (unit < text.length()) {
            int width = (Character.isHighSurrogate(text.charAt(unit))
                    && unit + 1 < text.length()
                    && Character.isLowSurrogate(text.charAt(unit + 1))) ? 2 : 1;
            map[unit] = codePoint;
            if (width == 2) {
                map[unit + 1] = codePoint;
            }
            unit += width;
            codePoint++;
        }
        map[text.length()] = codePoint;
        return map;
    }

    private static int toCodePointIndex(int[] map, int utf16Index) {
        if (map == null) {
            return utf16Index;
        }
        return map[Math.min(utf16Index, map.length - 1)];
    }

    private static void handleDlq(Jedis jedis, String taskJson, String errorMessage) {
        try {
            JsonNode root = MAPPER.readTree(taskJson);
            if (root instanceof ObjectNode) {
                ObjectNode node = (ObjectNode) root;
                int attempts = node.has("attempt_count") ? node.get("attempt_count").asInt() : 0;
                node.put("attempt_count", attempts + 1);
                node.put("error_reason", errorMessage);
                jedis.lpush(DEAD_QUEUE, MAPPER.writeValueAsString(node));
            }
        } catch (Exception ignored) {
            // Failsafe: never let the dead-letter path take the worker down.
        }
    }

    private static ObjectNode buildResult(String taskId, String engineId, boolean success,
                                          ArrayNode matches, double elapsedMs, String error) {
        ObjectNode result = MAPPER.createObjectNode();
        result.put("task_id", taskId);
        result.put("engine_id", engineId);
        result.put("success", success);
        result.set("matches", matches != null ? matches : MAPPER.createArrayNode());
        result.put("execution_time_ms", elapsedMs);
        if (error == null) {
            result.putNull("error");
        } else {
            result.put("error", error);
        }
        return result;
    }

    private static void publishResult(Jedis jedis, String taskId, ObjectNode result) {
        try {
            String json = MAPPER.writeValueAsString(result);
            if (json.getBytes(StandardCharsets.UTF_8).length > MAX_JSON_SIZE) {
                result = buildResult(taskId, result.get("engine_id").asText(), false, null,
                        result.get("execution_time_ms").asDouble(),
                        "Output JSON exceeds maximum allowed size of " + MAX_JSON_SIZE + " bytes.");
                json = MAPPER.writeValueAsString(result);
            }
            String key = "result:" + taskId;
            jedis.setex(key, 60, json);
            jedis.publish(key, "ready");
        } catch (Exception e) {
            System.err.println("[Error] Failed to publish result: " + e.getMessage());
        }
    }

    private static Pattern compile(String regex, JsonNode flagsNode) {
        StringBuilder flagKey = new StringBuilder();
        int flags = 0;
        if (flagsNode != null && flagsNode.isArray()) {
            Iterator<JsonNode> iterator = flagsNode.elements();
            while (iterator.hasNext()) {
                String flag = iterator.next().asText();
                flagKey.append(flag);
                if ("i".equals(flag)) {
                    flags |= Pattern.CASE_INSENSITIVE;
                } else if ("m".equals(flag)) {
                    flags |= Pattern.MULTILINE;
                } else if ("s".equals(flag)) {
                    flags |= Pattern.DOTALL;
                } else if ("d".equals(flag)) {
                    flags |= Pattern.UNIX_LINES;
                } else if ("u".equals(flag)) {
                    flags |= Pattern.UNICODE_CASE;
                } else if ("x".equals(flag)) {
                    flags |= Pattern.COMMENTS;
                } else if ("U".equals(flag)) {
                    flags |= Pattern.UNICODE_CHARACTER_CLASS;
                } else {
                    throw new IllegalArgumentException("Unsupported flag '" + flag + "' for the Java 8 engine");
                }
            }
        }

        String cacheKey = flagKey.toString() + "|" + regex;
        synchronized (CACHE) {
            Pattern cached = CACHE.get(cacheKey);
            if (cached != null) {
                return cached;
            }
        }
        Pattern compiled = Pattern.compile(regex, flags);
        synchronized (CACHE) {
            CACHE.put(cacheKey, compiled);
        }
        return compiled;
    }

    private static ArrayNode match(String regex, String text, JsonNode flagsNode) {
        if (text.length() > MAX_INPUT_SIZE) {
            throw new IllegalArgumentException("Input text exceeds maximum allowed size of " + MAX_INPUT_SIZE + " bytes.");
        }

        Pattern pattern = compile(regex, flagsNode);
        Matcher matcher = pattern.matcher(new InterruptibleCharSequence(text));
        int[] codePointMap = buildUtf16ToCodePointMap(text);

        ArrayNode matches = MAPPER.createArrayNode();
        int matchId = 0;
        while (matcher.find()) {
            if (matchId >= MAX_MATCHES) {
                throw new IllegalStateException("Exceeded maximum allowed matches (" + MAX_MATCHES + ").");
            }

            ObjectNode item = matches.addObject();
            item.put("match_id", matchId);
            item.put("full_match", matcher.group());
            item.put("start", toCodePointIndex(codePointMap, matcher.start()));
            item.put("end", toCodePointIndex(codePointMap, matcher.end()));

            ArrayNode groups = item.putArray("groups");
            for (int index = 1; index <= matcher.groupCount(); index++) {
                if (groups.size() >= MAX_GROUPS) {
                    throw new IllegalStateException("Exceeded maximum allowed groups per match (" + MAX_GROUPS + ").");
                }
                if (matcher.group(index) == null) {
                    continue;
                }
                ObjectNode group = groups.addObject();
                group.put("group_id", index);
                group.putNull("name");
                group.put("content", matcher.group(index));
                group.put("start", toCodePointIndex(codePointMap, matcher.start(index)));
                group.put("end", toCodePointIndex(codePointMap, matcher.end(index)));
            }
            matchId++;
        }
        return matches;
    }

    public static void listenAndProcess(String redisUrl) {
        System.out.println("[Worker] Java 8 worker listening on '" + QUEUE + "'...");

        Jedis jedis = new Jedis(redisUrl);
        Jedis publisher = new Jedis(redisUrl);

        while (true) {
            try {
                // Non-zero timeout keeps idle TCP connections from being dropped silently.
                List<String> popped = jedis.brpop(5, QUEUE);
                if (popped == null || popped.isEmpty()) {
                    continue;
                }

                String taskJson = popped.get(1);
                JsonNode root;
                try {
                    root = MAPPER.readTree(taskJson);
                } catch (Exception e) {
                    handleDlq(jedis, taskJson, "JSON Parse error: " + e.getMessage());
                    continue;
                }

                final String taskId = root.path("task_id").asText("");
                final String engineId = root.path("engine_id").asText("");
                final String regex = root.path("regex").asText("");
                final JsonNode flagsNode = root.get("flags");

                String text = root.path("text").asText("");
                String payloadId = root.hasNonNull("text_payload_id") ? root.get("text_payload_id").asText() : null;
                if (payloadId != null && !payloadId.isEmpty()) {
                    text = jedis.get(payloadId);
                    if (text == null) {
                        String message = "Payload expired or missing from Redis";
                        handleDlq(jedis, taskJson, message);
                        publishResult(publisher, taskId, buildResult(taskId, engineId, false, null, 0.0, message));
                        continue;
                    }
                }

                final String resolvedText = text;
                long startedAt = System.nanoTime();

                Future<ArrayNode> future = EXECUTOR.submit(new Callable<ArrayNode>() {
                    public ArrayNode call() {
                        return match(regex, resolvedText, flagsNode);
                    }
                });

                ObjectNode result;
                try {
                    ArrayNode matches = future.get(TIMEOUT_MS, TimeUnit.MILLISECONDS);
                    double elapsed = (System.nanoTime() - startedAt) / 1_000_000.0;
                    result = buildResult(taskId, engineId, true, matches, elapsed, null);
                } catch (TimeoutException e) {
                    future.cancel(true);
                    String message = "TIMEOUT: " + engineId + " execution exceeded " + TIMEOUT_MS + "ms SLA.";
                    handleDlq(jedis, taskJson, message);
                    result = buildResult(taskId, engineId, false, null, TIMEOUT_MS, message);
                } catch (Exception e) {
                    Throwable cause = e.getCause() != null ? e.getCause() : e;
                    String message = cause.getMessage() != null ? cause.getMessage() : cause.toString();
                    handleDlq(jedis, taskJson, message);
                    double elapsed = (System.nanoTime() - startedAt) / 1_000_000.0;
                    result = buildResult(taskId, engineId, false, null, elapsed, message);
                }

                publishResult(publisher, taskId, result);
            } catch (Exception e) {
                System.err.println("[Error] Java 8 worker loop failure: " + e.getMessage());
                try {
                    jedis.close();
                    publisher.close();
                } catch (Exception ignored) {
                    // best effort
                }
                jedis = new Jedis(redisUrl);
                publisher = new Jedis(redisUrl);
                try {
                    Thread.sleep(2000L);
                } catch (InterruptedException interrupted) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
    }
}
