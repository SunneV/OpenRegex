# frozen_string_literal: true

require 'redis'

require_relative 'registry'
require_relative 'processor'

WORKERS_HASH_KEY = 'openregex:workers'
HEARTBEAT_TTL_S = 15
HEARTBEAT_INTERVAL_S = 5

redis_url = ENV.fetch('REDIS_URL', 'redis://redis:6379')

# Ruby 3.2+ aborts a match that blows past the budget, which is the ReDoS guard
# for this worker; there is no separate supervisor process.
timeout_ms = Integer(ENV.fetch('WORKER_EXECUTION_TIMEOUT_MS', '1000'))
Regexp.timeout = timeout_ms / 1000.0

main_redis = Redis.new(url: redis_url)
heartbeat_redis = Redis.new(url: redis_url)
shutdown_redis = Redis.new(url: redis_url)

def set_heartbeat(redis)
  redis.setex(OpenRegex::Processor::HEARTBEAT_KEY, HEARTBEAT_TTL_S, Time.now.to_i.to_s)
rescue StandardError
  # transient Redis outage; the TTL just expires until it recovers
end

# The heartbeat must be live before registration so discovery never sees a
# registered worker without one.
set_heartbeat(main_redis)
main_redis.hset(WORKERS_HASH_KEY, OpenRegex::Registry::WORKER_NAME,
                JSON.generate(OpenRegex::Registry.worker_info))
puts "[Worker] Registered '#{OpenRegex::Registry::WORKER_NAME}' with 1 engine."
$stdout.flush

Thread.new do
  loop do
    sleep HEARTBEAT_INTERVAL_S
    set_heartbeat(heartbeat_redis)
  end
end

# Graceful unregister on shutdown (docker stop / Ctrl+C).
unregister = proc do
  begin
    shutdown_redis.hdel(WORKERS_HASH_KEY, OpenRegex::Registry::WORKER_NAME)
    shutdown_redis.del(OpenRegex::Processor::HEARTBEAT_KEY)
  rescue StandardError
    # best effort
  end
  exit!(0)
end

%w[TERM INT].each do |signal|
  Signal.trap(signal) { Thread.new(&unregister) }
end

OpenRegex::Processor.listen_and_process(main_redis)
