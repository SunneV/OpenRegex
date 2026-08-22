package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/redis/go-redis/v9"
)

const workerName = "worker-go"
const workersHashKey = "openregex:workers"
const heartbeatKey = "openregex:workers:heartbeat:" + workerName
const heartbeatTTL = 15 * time.Second
const heartbeatInterval = 5 * time.Second

func setHeartbeat(ctx context.Context, client *redis.Client) {
	client.SetEx(ctx, heartbeatKey, fmt.Sprintf("%d", time.Now().Unix()), heartbeatTTL)
}

func startHeartbeat(client *redis.Client) {
	go func() {
		ctx := context.Background()
		for {
			time.Sleep(heartbeatInterval)
			setHeartbeat(ctx, client)
		}
	}()
}

func installShutdownUnregister(client *redis.Client) {
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGTERM, os.Interrupt)
	go func() {
		<-sigs
		ctx := context.Background()
		client.HDel(ctx, workersHashKey, workerName)
		client.Del(ctx, heartbeatKey)
		os.Exit(0)
	}()
}

func main() {
	redisUrl := os.Getenv("REDIS_URL")
	if redisUrl == "" {
		redisUrl = "redis://redis:6379"
	}

	opts, err := redis.ParseURL(redisUrl)
	if err != nil {
		log.Fatalf("Failed to parse REDIS_URL: %v", err)
	}

	client := redis.NewClient(opts)

	ctx := context.Background()

	// Heartbeat must be live before registration so discovery never sees
	// a registered worker without one.
	setHeartbeat(ctx, client)
	if err := registerEngines(ctx, client); err != nil {
		log.Fatalf("Failed to register engines: %v", err)
	}
	startHeartbeat(client)
	installShutdownUnregister(client)

	listenAndProcess(client)
}
