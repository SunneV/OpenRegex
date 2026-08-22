package com.openregex;

import redis.clients.jedis.Jedis;

public class WorkerRunner {
    private static final String WORKER_NAME = "worker-jvm";
    private static final String WORKERS_HASH_KEY = "openregex:workers";
    private static final String HEARTBEAT_KEY = "openregex:workers:heartbeat:" + WORKER_NAME;
    private static final long HEARTBEAT_TTL_S = 15L;
    private static final long HEARTBEAT_INTERVAL_MS = 5000L;

    private static void setHeartbeat(Jedis jedis) {
        try {
            jedis.setex(HEARTBEAT_KEY, HEARTBEAT_TTL_S, String.valueOf(System.currentTimeMillis() / 1000));
        } catch (Exception ignored) {
            // transient Redis outage; the TTL just expires until it recovers
        }
    }

    public static void main(String[] args) {
        String redisUrl = System.getenv("REDIS_URL");
        if (redisUrl == null || redisUrl.isEmpty()) {
            redisUrl = "redis://redis:6379";
        }
        final String finalRedisUrl = redisUrl;

        // Heartbeat must be live before registration so discovery never sees
        // a registered worker without one.
        try (Jedis jedis = new Jedis(finalRedisUrl)) {
            setHeartbeat(jedis);
            Registry.registerEngines(jedis);
        } catch (Exception e) {
            System.err.println("Failed to register engines: " + e.getMessage());
        }

        Thread heartbeat = new Thread(() -> {
            try (Jedis hbJedis = new Jedis(finalRedisUrl)) {
                while (!Thread.currentThread().isInterrupted()) {
                    try {
                        Thread.sleep(HEARTBEAT_INTERVAL_MS);
                    } catch (InterruptedException e) {
                        return;
                    }
                    setHeartbeat(hbJedis);
                }
            }
        }, "worker-heartbeat");
        heartbeat.setDaemon(true);
        heartbeat.start();

        // Graceful unregister on shutdown (docker stop / Ctrl+C).
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            try (Jedis jedis = new Jedis(finalRedisUrl)) {
                jedis.hdel(WORKERS_HASH_KEY, WORKER_NAME);
                jedis.del(HEARTBEAT_KEY);
            } catch (Exception ignored) {
            }
        }, "worker-unregister"));

        Processor.listenAndProcess(finalRedisUrl);
    }
}
