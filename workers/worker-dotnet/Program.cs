using System;
using StackExchange.Redis;
using OpenRegex.Worker;

const string WorkerName = "worker-dotnet";
const string WorkersHashKey = "openregex:workers";
const string HeartbeatKey = "openregex:workers:heartbeat:" + WorkerName;
var heartbeatTtl = TimeSpan.FromSeconds(15);
var heartbeatInterval = TimeSpan.FromSeconds(5);

var redisUrl = Environment.GetEnvironmentVariable("REDIS_URL") ?? "redis://redis:6379";
if (redisUrl.StartsWith("redis://"))
{
    redisUrl = redisUrl.Substring(8);
}

var redis = await ConnectionMultiplexer.ConnectAsync(redisUrl);
var db = redis.GetDatabase();
var pubSub = redis.GetSubscriber();

async Task SetHeartbeatAsync()
{
    try
    {
        await db.StringSetAsync(HeartbeatKey, DateTimeOffset.UtcNow.ToUnixTimeSeconds(), heartbeatTtl);
    }
    catch
    {
        // transient Redis outage; the TTL just expires until it recovers
    }
}

void Unregister()
{
    try
    {
        db.HashDelete(WorkersHashKey, WorkerName);
        db.KeyDelete(HeartbeatKey);
    }
    catch
    {
        // best effort
    }
}

// Heartbeat must be live before registration so discovery never sees
// a registered worker without one.
await SetHeartbeatAsync();
await Registry.RegisterEnginesAsync(db);

_ = Task.Run(async () =>
{
    while (true)
    {
        await Task.Delay(heartbeatInterval);
        await SetHeartbeatAsync();
    }
});

// Graceful unregister on shutdown (docker stop / Ctrl+C).
AppDomain.CurrentDomain.ProcessExit += (_, _) => Unregister();
Console.CancelKeyPress += (_, e) =>
{
    Unregister();
    Environment.Exit(0);
};

await Processor.ListenAndProcessAsync(db, pubSub);
