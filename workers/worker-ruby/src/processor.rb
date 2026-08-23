# frozen_string_literal: true

require 'json'

module OpenRegex
  # Redis queue consumer executing patterns on Ruby's built-in Onigmo engine.
  module Processor
    QUEUE = 'queue:ruby'
    DEAD_QUEUE = 'queue:ruby:dead'
    HEARTBEAT_KEY = 'openregex:workers:heartbeat:worker-ruby'

    TIMEOUT_MS = Integer(ENV.fetch('WORKER_EXECUTION_TIMEOUT_MS', '1000'))
    MAX_INPUT_SIZE = Integer(ENV.fetch('WORKER_MAX_INPUT_SIZE', '10485760'))
    MAX_MATCHES = Integer(ENV.fetch('WORKER_MAX_MATCHES', '10000'))
    MAX_GROUPS = Integer(ENV.fetch('WORKER_MAX_GROUPS', '1000'))
    MAX_JSON_SIZE = Integer(ENV.fetch('WORKER_MAX_JSON_SIZE', '10485760'))

    FLAG_BITS = {
      'i' => Regexp::IGNORECASE,
      'm' => Regexp::MULTILINE,
      'x' => Regexp::EXTENDED
    }.freeze

    def self.build_options(flags)
      options = 0
      Array(flags).each do |flag|
        next if flag.nil? || flag.empty?
        # 'o' (compile once) is a literal-syntax modifier with no Regexp.new
        # counterpart; accept it so the UI flag set stays honest.
        next if flag == 'o'

        bit = FLAG_BITS[flag]
        raise ArgumentError, "Unsupported flag '#{flag}' for the Ruby engine" if bit.nil?

        options |= bit
      end
      options
    end

    # Ruby drops numbered capturing as soon as a named group is present, so the
    # n-th group is exactly the n-th declared name in that case.
    def self.group_names(regexp)
      names = regexp.names
      names.empty? ? nil : names
    end

    def self.execute(req)
      text = req['text'].to_s
      raise ArgumentError, "Input text exceeds maximum allowed size of #{MAX_INPUT_SIZE} bytes." if text.bytesize > MAX_INPUT_SIZE

      regexp = Regexp.new(req['regex'].to_s, build_options(req['flags']))
      names = group_names(regexp)

      matches = []
      position = 0
      text_length = text.length

      while position <= text_length
        data = regexp.match(text, position)
        break if data.nil?

        raise ArgumentError, "Exceeded maximum allowed matches (#{MAX_MATCHES})." if matches.length >= MAX_MATCHES

        groups = []
        (1...data.size).each do |index|
          raise ArgumentError, "Exceeded maximum allowed groups per match (#{MAX_GROUPS})." if groups.length >= MAX_GROUPS
          next if data[index].nil?

          groups << {
            'group_id' => index,
            'name' => names ? names[index - 1] : nil,
            'content' => data[index],
            'start' => data.begin(index),
            'end' => data.end(index)
          }
        end

        matches << {
          'match_id' => matches.length,
          'full_match' => data[0],
          'start' => data.begin(0),
          'end' => data.end(0),
          'groups' => groups
        }

        # Zero-width matches would otherwise pin the scanner in place.
        position = data.end(0) > data.begin(0) ? data.end(0) : data.begin(0) + 1
      end

      matches
    end

    def self.handle_dlq(redis, task, error_message)
      task = {} unless task.is_a?(Hash)
      task['attempt_count'] = task.fetch('attempt_count', 0) + 1
      task['error_reason'] = error_message
      redis.lpush(DEAD_QUEUE, JSON.generate(task))
    rescue StandardError
      # Failsafe: never let the dead-letter path take the worker down.
    end

    def self.publish(redis, task_id, result)
      json = JSON.generate(result)
      if json.bytesize > MAX_JSON_SIZE
        result = result.merge(
          'success' => false,
          'matches' => [],
          'error' => "Output JSON exceeds maximum allowed size of #{MAX_JSON_SIZE} bytes."
        )
        json = JSON.generate(result)
      end
      redis.setex("result:#{task_id}", 60, json)
      redis.publish("result:#{task_id}", 'ready')
    end

    def self.process_task(redis, raw_json)
      task = JSON.parse(raw_json)

      payload_id = task['text_payload_id']
      if payload_id && !payload_id.to_s.empty?
        payload = redis.get(payload_id)
        if payload.nil?
          message = 'Payload expired or missing from Redis'
          handle_dlq(redis, task, message)
          publish(redis, task['task_id'], {
                    'task_id' => task['task_id'], 'engine_id' => task['engine_id'], 'success' => false,
                    'matches' => [], 'execution_time_ms' => 0.0, 'error' => message
                  })
          return
        end
        task['text'] = payload
      end

      started = Process.clock_gettime(Process::CLOCK_MONOTONIC)
      matches = []
      error = nil

      begin
        matches = execute(task)
      rescue Regexp::TimeoutError
        error = "TIMEOUT: #{task['engine_id']} execution exceeded #{TIMEOUT_MS}ms SLA."
        handle_dlq(redis, task, error)
      rescue StandardError => e
        error = e.message
        handle_dlq(redis, task, error)
      end

      elapsed = (Process.clock_gettime(Process::CLOCK_MONOTONIC) - started) * 1000.0

      publish(redis, task['task_id'], {
                'task_id' => task['task_id'],
                'engine_id' => task['engine_id'],
                'success' => error.nil?,
                'matches' => error.nil? ? matches : [],
                'execution_time_ms' => elapsed,
                'error' => error
              })
    rescue StandardError => e
      warn "[Error] Task processing failure: #{e.message}"
      handle_dlq(redis, nil, e.message)
    end

    def self.listen_and_process(redis)
      puts "[Worker] Ruby worker listening on '#{QUEUE}'..."
      $stdout.flush

      loop do
        begin
          entry = redis.brpop(QUEUE, timeout: 5)
          next if entry.nil?

          process_task(redis, entry[1])
        rescue StandardError => e
          warn "[Error] Ruby worker loop failure: #{e.message}"
          sleep 2
        end
      end
    end
  end
end
