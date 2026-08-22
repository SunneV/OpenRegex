import { Redis } from "ioredis";
import { registerEngines } from "./registry.js";
import { listenAndProcess } from "./processor.js";
import { WORKER_INFO } from "./engines/index.js";

const WORKERS_HASH_KEY = "openregex:workers";
const HEARTBEAT_KEY = `openregex:workers:heartbeat:${WORKER_INFO.worker_name}`;
const HEARTBEAT_TTL_S = 15;
const HEARTBEAT_INTERVAL_MS = 5000;

async function setHeartbeat(redisClient) {
  try {
    await redisClient.set(HEARTBEAT_KEY, Math.floor(Date.now() / 1000), "EX", HEARTBEAT_TTL_S);
  } catch {
    // transient Redis outage; the TTL just expires until it recovers
  }
}

function installShutdownUnregister(redisClient) {
  const shutdown = async () => {
    try {
      await redisClient.hdel(WORKERS_HASH_KEY, WORKER_INFO.worker_name);
      await redisClient.del(HEARTBEAT_KEY);
    } catch {
      // best effort
    }
    process.exit(0);
  };
  process.on("SIGTERM", shutdown);
  process.on("SIGINT", shutdown);
}

async function main() {
  const redisUrl = process.env.REDIS_URL || "redis://redis:6379";
  const redisClient = new Redis(redisUrl);
  const pubClient = new Redis(redisUrl);

  // Heartbeat must be live before registration so discovery never sees
  // a registered worker without one.
  await setHeartbeat(redisClient);
  await registerEngines(redisClient);
  setInterval(() => setHeartbeat(redisClient), HEARTBEAT_INTERVAL_MS);
  installShutdownUnregister(redisClient);

  await listenAndProcess(redisClient, pubClient);
}

main().catch(console.error);
