<?php

require __DIR__ . '/../vendor/autoload.php';

use OpenRegex\Worker\Registry;
use OpenRegex\Worker\Processor;

$redisUrl = getenv('REDIS_URL') ?: 'redis://redis:6379';
$client = new Predis\Client($redisUrl);

// Graceful unregister on shutdown (docker stop / Ctrl+C).
if (function_exists('pcntl_async_signals')) {
    pcntl_async_signals(true);
    $unregister = function () use ($client) {
        try {
            $client->hdel('openregex:workers', ['worker-php']);
            $client->del(['openregex:workers:heartbeat:worker-php']);
        } catch (\Exception $e) {
            // best effort
        }
        exit(0);
    };
    pcntl_signal(SIGTERM, $unregister);
    pcntl_signal(SIGINT, $unregister);
}

try {
    // Heartbeat must be live before registration so discovery never sees
    // a registered worker without one.
    $client->setex('openregex:workers:heartbeat:worker-php', 15, (string)time());
    Registry::registerEngines($client);
    Processor::listenAndProcess($client);
} catch (\Exception $e) {
    echo "Fatal error during startup: " . $e->getMessage() . "\n";
    exit(1);
}