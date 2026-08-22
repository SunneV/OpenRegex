mod models;
mod processor;
mod registry;

use std::env;

const WORKER_NAME: &str = "worker-rust";
const WORKERS_HASH_KEY: &str = "openregex:workers";
const HEARTBEAT_KEY: &str = "openregex:workers:heartbeat:worker-rust";
const HEARTBEAT_TTL_S: usize = 15;
const HEARTBEAT_INTERVAL_S: u64 = 5;

fn unix_now() -> u64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0)
}

async fn set_heartbeat(con: &mut redis::aio::MultiplexedConnection) {
    let _: redis::RedisResult<()> = redis::cmd("SETEX")
        .arg(HEARTBEAT_KEY)
        .arg(HEARTBEAT_TTL_S)
        .arg(unix_now())
        .query_async(con)
        .await;
}

async fn unregister(client: &redis::Client) {
    if let Ok(mut con) = client.get_multiplexed_tokio_connection().await {
        let _: redis::RedisResult<()> = redis::cmd("HDEL")
            .arg(WORKERS_HASH_KEY)
            .arg(WORKER_NAME)
            .query_async(&mut con)
            .await;
        let _: redis::RedisResult<()> = redis::cmd("DEL")
            .arg(HEARTBEAT_KEY)
            .query_async(&mut con)
            .await;
    }
}

#[tokio::main]
async fn main() -> redis::RedisResult<()> {
    let redis_url = env::var("REDIS_URL").unwrap_or_else(|_| "redis://redis:6379".to_string());
    let client = redis::Client::open(redis_url)?;

    // Use multiplexed connection for simple registration.
    // The heartbeat must be live before registering so discovery never sees
    // a registered worker without one.
    let mut con = client.get_multiplexed_tokio_connection().await?;
    set_heartbeat(&mut con).await;
    registry::register_engines(&mut con).await?;

    let mut hb_con = client.get_multiplexed_tokio_connection().await?;
    tokio::spawn(async move {
        loop {
            tokio::time::sleep(std::time::Duration::from_secs(HEARTBEAT_INTERVAL_S)).await;
            set_heartbeat(&mut hb_con).await;
        }
    });

    // Graceful unregister on shutdown signals (docker stop / Ctrl+C).
    let sig_client = client.clone();
    tokio::spawn(async move {
        #[cfg(unix)]
        {
            use tokio::signal::unix::{signal, SignalKind};
            let mut term = signal(SignalKind::terminate()).expect("SIGTERM handler");
            tokio::select! {
                _ = tokio::signal::ctrl_c() => {},
                _ = term.recv() => {},
            }
        }
        #[cfg(not(unix))]
        {
            let _ = tokio::signal::ctrl_c().await;
        }
        unregister(&sig_client).await;
        std::process::exit(0);
    });

    // Pass the client to the processor so it can spawn dedicated connections
    processor::listen_and_process(client).await;

    Ok(())
}