package com.openregex.jvm8;

import redis.clients.jedis.Jedis;

public final class WorkerRunner {

    private static final String WORKERS_HASH_KEY = "openregex:workers";
    private static final String HEARTBEAT_KEY = "openregex:workers:heartbeat:" + Registry.WORKER_NAME;
    private static final int HEARTBEAT_TTL_S = 15;
    private static final long HEARTBEAT_INTERVAL_MS = 5000L;

    private WorkerRunner() {
    }

    private static void setHeartbeat(Jedis jedis) {
        try {
            jedis.setex(HEARTBEAT_KEY, HEARTBEAT_TTL_S, String.valueOf(System.currentTimeMillis() / 1000L));
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
        Jedis registrar = new Jedis(finalRedisUrl);
        try {
            setHeartbeat(registrar);
            Registry.registerEngines(registrar);
        } catch (Exception e) {
            System.err.println("Failed to register engines: " + e.getMessage());
        } finally {
            registrar.close();
        }

        Thread heartbeat = new Thread(new Runnable() {
            public void run() {
                Jedis beat = new Jedis(finalRedisUrl);
                while (!Thread.currentThread().isInterrupted()) {
                    try {
                        Thread.sleep(HEARTBEAT_INTERVAL_MS);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        return;
                    }
                    setHeartbeat(beat);
                }
            }
        }, "worker-heartbeat");
        heartbeat.setDaemon(true);
        heartbeat.start();

        // Graceful unregister on shutdown (docker stop / Ctrl+C).
        Runtime.getRuntime().addShutdownHook(new Thread(new Runnable() {
            public void run() {
                Jedis jedis = new Jedis(finalRedisUrl);
                try {
                    jedis.hdel(WORKERS_HASH_KEY, Registry.WORKER_NAME);
                    jedis.del(HEARTBEAT_KEY);
                } catch (Exception ignored) {
                    // best effort
                } finally {
                    jedis.close();
                }
            }
        }, "worker-unregister"));

        Processor.listenAndProcess(finalRedisUrl);
    }
}
