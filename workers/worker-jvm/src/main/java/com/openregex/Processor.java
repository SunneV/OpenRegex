package com.openregex;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.openregex.models.Models.MatchGroup;
import com.openregex.models.Models.MatchItem;
import com.openregex.models.Models.MatchRequest;
import com.openregex.models.Models.MatchResult;
import redis.clients.jedis.Jedis;

import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.*;

public class Processor {
    private static final ObjectMapper mapper = new ObjectMapper()
            .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

    private static final int TIMEOUT_MS = getEnvInt("WORKER_EXECUTION_TIMEOUT_MS", 1000);
    private static final int MAX_INPUT_SIZE = getEnvInt("WORKER_MAX_INPUT_SIZE", 10485760);
    private static final int MAX_MATCHES = getEnvInt("WORKER_MAX_MATCHES", 10000);
    private static final int MAX_GROUPS = getEnvInt("WORKER_MAX_GROUPS", 1000);
    private static final int MAX_JSON_SIZE = getEnvInt("WORKER_MAX_JSON_SIZE", 10485760);

    private static final ExecutorService executor = Executors.newCachedThreadPool();

    private static int getEnvInt(String key, int defaultValue) {
        String val = System.getenv(key);
        if (val != null && !val.isEmpty()) {
            try {
                return Integer.parseInt(val);
            } catch (NumberFormatException ignored) {}
        }
        return defaultValue;
    }

    private static class LRUCache<K, V> extends LinkedHashMap<K, V> {
        private final int maxEntries;
        public LRUCache(int maxEntries) {
            super(maxEntries + 1, 1.0f, true);
            this.maxEntries = maxEntries;
        }
        @Override
        protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
            return size() > maxEntries;
        }
    }

    private static final LRUCache<String, java.util.regex.Pattern> stdCache = new LRUCache<>(1000);
    private static final LRUCache<String, com.google.re2j.Pattern> re2jCache = new LRUCache<>(1000);

    private static class InterruptibleCharSequence implements CharSequence {
        private final CharSequence inner;

        public InterruptibleCharSequence(CharSequence inner) {
            this.inner = inner;
        }

        @Override
        public int length() {
            return inner.length();
        }

        @Override
        public char charAt(int index) {
            if (Thread.currentThread().isInterrupted()) {
                throw new RuntimeException("TIMEOUT: JVM execution exceeded SLA.");
            }
            return inner.charAt(index);
        }

        @Override
        public CharSequence subSequence(int start, int end) {
            return new InterruptibleCharSequence(inner.subSequence(start, end));
        }

        @Override
        public String toString() {
            return inner.toString();
        }
    }

    // java.util.regex and RE2J report UTF-16 code unit offsets; the platform
    // contract requires Unicode code point indices. Returns null when the text
    // contains no surrogate pairs (offsets already equal code point indices).
    private static int[] buildUtf16ToCodePointMap(String text) {
        if (text.length() == text.codePointCount(0, text.length())) {
            return null;
        }
        int[] map = new int[text.length() + 1];
        int cp = 0;
        int u = 0;
        while (u < text.length()) {
            int width = (Character.isHighSurrogate(text.charAt(u))
                    && u + 1 < text.length()
                    && Character.isLowSurrogate(text.charAt(u + 1))) ? 2 : 1;
            map[u] = cp;
            if (width == 2) {
                map[u + 1] = cp;
            }
            u += width;
            cp++;
        }
        map[text.length()] = cp;
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
            JsonNode rootNode = mapper.readTree(taskJson);
            if (rootNode instanceof ObjectNode objNode) {
                int attemptCount = objNode.has("attempt_count") ? objNode.get("attempt_count").asInt() : 0;
                objNode.put("attempt_count", attemptCount + 1);
                objNode.put("error_reason", errorMessage);
                jedis.lpush("queue:jvm:dead", mapper.writeValueAsString(objNode));
            }
        } catch (Exception ignored) {}
    }

    private static void publishResult(Jedis jedis, String taskId, MatchResult result) {
        try {
            String resJson = mapper.writeValueAsString(result);
            if (resJson.getBytes(StandardCharsets.UTF_8).length > MAX_JSON_SIZE) {
                result = new MatchResult(result.task_id(), result.engine_id(), false, List.of(), result.execution_time_ms(), "Output JSON exceeds maximum allowed size of " + MAX_JSON_SIZE + " bytes.");
                resJson = mapper.writeValueAsString(result);
            }
            String key = "result:" + taskId;
            jedis.setex(key, 60, resJson);
            jedis.publish(key, "ready");
        } catch (Exception e) {
            System.err.println("[Error] Failed to publish result: " + e.getMessage());
        }
    }

    public static void listenAndProcess(String redisUrl) {
        System.out.println("[Worker] JVM worker listening on 'queue:jvm'...");

        try (Jedis jedis = new Jedis(redisUrl);
             Jedis pubJedis = new Jedis(redisUrl)) {

            while (true) {
                List<String> popResult = jedis.brpop(0, "queue:jvm");

                if (popResult == null || popResult.isEmpty()) continue;

                String taskJson = popResult.get(1);
                JsonNode rootNode;
                MatchRequest rawReq;

                try {
                    rootNode = mapper.readTree(taskJson);
                    rawReq = mapper.treeToValue(rootNode, MatchRequest.class);
                } catch (Exception e) {
                    handleDlq(jedis, taskJson, "JSON Parse error: " + e.getMessage());
                    continue;
                }

                String textPayloadId = rootNode.hasNonNull("text_payload_id") ? rootNode.get("text_payload_id").asText() : null;

                String resolvedText = rawReq.text();
                if (textPayloadId != null && !textPayloadId.isEmpty()) {
                    resolvedText = jedis.get(textPayloadId);
                    if (resolvedText == null) {
                        String errMsg = "Payload expired or missing from Redis";
                        handleDlq(jedis, taskJson, errMsg);
                        MatchResult errRes = new MatchResult(rawReq.task_id(), rawReq.engine_id(), false, List.of(), 0.0, errMsg);
                        publishResult(pubJedis, rawReq.task_id(), errRes);
                        continue;
                    }
                }

                MatchRequest req = new MatchRequest(rawReq.task_id(), rawReq.engine_id(), rawReq.regex(), resolvedText, rawReq.flags());

                long startTime = System.nanoTime();

                Future<MatchResult> future = executor.submit(() -> executeRegex(req, startTime));
                MatchResult result;

                try {
                    result = future.get(TIMEOUT_MS, TimeUnit.MILLISECONDS);
                } catch (TimeoutException e) {
                    future.cancel(true);
                    handleDlq(jedis, taskJson, "TIMEOUT: JVM execution exceeded SLA.");
                    result = new MatchResult(req.task_id(), req.engine_id(), false, List.of(), TIMEOUT_MS, "TIMEOUT: JVM execution exceeded " + TIMEOUT_MS + "ms SLA.");
                } catch (Exception e) {
                    handleDlq(jedis, taskJson, e.getMessage());
                    result = new MatchResult(req.task_id(), req.engine_id(), false, List.of(), 0.0, e.getMessage());
                }

                publishResult(pubJedis, req.task_id(), result);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static MatchResult executeRegex(MatchRequest req, long startTime) {
        List<MatchItem> matchItems = new ArrayList<>();

        try {
            if (req.text().length() > MAX_INPUT_SIZE) {
                throw new IllegalArgumentException("Input text exceeds maximum allowed size of " + MAX_INPUT_SIZE + " bytes.");
            }

            String cacheKey = req.flags().toString() + "|" + req.regex();

            if ("jvm_standard".equals(req.engine_id())) {
                java.util.regex.Pattern p;
                synchronized (stdCache) {
                    p = stdCache.get(cacheKey);
                    if (p == null) {
                        int flags = 0;
                        for (String f : req.flags()) {
                            switch (f) {
                                case "i" -> flags |= java.util.regex.Pattern.CASE_INSENSITIVE;
                                case "m" -> flags |= java.util.regex.Pattern.MULTILINE;
                                case "s" -> flags |= java.util.regex.Pattern.DOTALL;
                                case "x" -> flags |= java.util.regex.Pattern.COMMENTS;
                            }
                        }
                        p = java.util.regex.Pattern.compile(req.regex(), flags);
                        stdCache.put(cacheKey, p);
                    }
                }

                java.util.regex.Matcher m = p.matcher(new InterruptibleCharSequence(req.text()));
                int[] cpMap = buildUtf16ToCodePointMap(req.text());

                int matchId = 0;
                while (m.find()) {
                    if (matchId >= MAX_MATCHES) {
                        throw new IllegalStateException("Exceeded maximum allowed matches (" + MAX_MATCHES + ").");
                    }
                    List<MatchGroup> groups = new ArrayList<>();
                    for (int i = 1; i <= m.groupCount(); i++) {
                        if (groups.size() >= MAX_GROUPS) {
                            throw new IllegalStateException("Exceeded maximum allowed groups per match (" + MAX_GROUPS + ").");
                        }
                        if (m.group(i) != null) {
                            groups.add(new MatchGroup(i, null, m.group(i), toCodePointIndex(cpMap, m.start(i)), toCodePointIndex(cpMap, m.end(i))));
                        }
                    }
                    matchItems.add(new MatchItem(matchId++, m.group(), toCodePointIndex(cpMap, m.start()), toCodePointIndex(cpMap, m.end()), groups));
                }
            } else if ("jvm_re2j".equals(req.engine_id())) {
                com.google.re2j.Pattern p;
                synchronized (re2jCache) {
                    p = re2jCache.get(cacheKey);
                    if (p == null) {
                        int flags = 0;
                        for (String f : req.flags()) {
                            switch (f) {
                                case "i" -> flags |= com.google.re2j.Pattern.CASE_INSENSITIVE;
                                case "m" -> flags |= com.google.re2j.Pattern.MULTILINE;
                                case "s" -> flags |= com.google.re2j.Pattern.DOTALL;
                            }
                        }
                        p = com.google.re2j.Pattern.compile(req.regex(), flags);
                        re2jCache.put(cacheKey, p);
                    }
                }

                com.google.re2j.Matcher m = p.matcher(req.text());
                int[] cpMap = buildUtf16ToCodePointMap(req.text());

                int matchId = 0;
                while (m.find()) {
                    if (matchId >= MAX_MATCHES) {
                        throw new IllegalStateException("Exceeded maximum allowed matches (" + MAX_MATCHES + ").");
                    }
                    List<MatchGroup> groups = new ArrayList<>();
                    for (int i = 1; i <= m.groupCount(); i++) {
                        if (groups.size() >= MAX_GROUPS) {
                            throw new IllegalStateException("Exceeded maximum allowed groups per match (" + MAX_GROUPS + ").");
                        }
                        if (m.group(i) != null) {
                            groups.add(new MatchGroup(i, null, m.group(i), toCodePointIndex(cpMap, m.start(i)), toCodePointIndex(cpMap, m.end(i))));
                        }
                    }
                    matchItems.add(new MatchItem(matchId++, m.group(), toCodePointIndex(cpMap, m.start()), toCodePointIndex(cpMap, m.end()), groups));
                }
            } else {
                throw new IllegalArgumentException("Unknown JVM engine: " + req.engine_id());
            }

            double execTime = (System.nanoTime() - startTime) / 1_000_000.0;
            return new MatchResult(req.task_id(), req.engine_id(), true, matchItems, execTime, null);
        } catch (Exception e) {
            double execTime = (System.nanoTime() - startTime) / 1_000_000.0;
            return new MatchResult(req.task_id(), req.engine_id(), false, List.of(), execTime, e.getMessage());
        }
    }
}