<?php

namespace OpenRegex\Worker;

class Processor {
    private static function handleDlq($client, $taskDict, $errorMessage) {
        try {
            if (is_array($taskDict)) {
                $taskDict['attempt_count'] = isset($taskDict['attempt_count']) ? $taskDict['attempt_count'] + 1 : 1;
                $taskDict['error_reason'] = $errorMessage;
                $client->lpush("queue:php:dead", json_encode($taskDict));
            }
        } catch (\Exception $e) {
            // Failsafe
        }
    }

    public static function listenAndProcess($client) {
        echo "[Worker] PHP worker listening on 'queue:php'...\n";

        $maxInputSize = (int)(getenv('WORKER_MAX_INPUT_SIZE') ?: 10485760);
        $maxMatches = (int)(getenv('WORKER_MAX_MATCHES') ?: 10000);
        $maxGroups = (int)(getenv('WORKER_MAX_GROUPS') ?: 1000);
        $maxJsonSize = (int)(getenv('WORKER_MAX_JSON_SIZE') ?: 10485760);

        // PHP is single-threaded, so the TTL heartbeat is refreshed from the
        // poll loop; brpop's 5s timeout keeps refreshes within the 15s TTL.
        $heartbeatKey = 'openregex:workers:heartbeat:worker-php';
        $lastBeat = 0;

        while (true) {
            try {
                if (time() - $lastBeat >= 5) {
                    try {
                        $client->setex($heartbeatKey, 15, (string)time());
                    } catch (\Exception $e) {
                        // transient Redis outage; the TTL just expires until it recovers
                    }
                    $lastBeat = time();
                }

                // Use a non-zero timeout to prevent silent TCP connection drops
                $result = $client->brpop(['queue:php'], 5);
                if (!$result) continue;

                $taskJson = $result[1];
                $req = json_decode($taskJson, true);
                if (!$req) {
                    self::handleDlq($client, [], "JSON Parse error");
                    continue;
                }

                // CLAIM-CHECK: Retrieve payload if text_payload_id is present
                if (!empty($req['text_payload_id'])) {
                    $payload = $client->get($req['text_payload_id']);
                    if ($payload === null) {
                        $errMsg = "Payload expired or missing from Redis";
                        self::handleDlq($client, $req, $errMsg);
                        $res = [
                            'task_id' => $req['task_id'],
                            'engine_id' => $req['engine_id'],
                            'success' => false,
                            'matches' => [],
                            'execution_time_ms' => 0.0,
                            'error' => $errMsg
                        ];
                        $client->setex("result:" . $req['task_id'], 60, json_encode($res));
                        $client->publish("result:" . $req['task_id'], "ready");
                        continue;
                    }
                    $req['text'] = $payload;
                }

                $start = microtime(true);

                $res = [
                    'task_id' => $req['task_id'],
                    'engine_id' => $req['engine_id'],
                    'success' => true,
                    'matches' => [],
                    'execution_time_ms' => 0.0,
                    'error' => null
                ];

                try {
                    if (strlen($req['text']) > $maxInputSize) {
                        throw new \Exception("Input text exceeds maximum allowed size of {$maxInputSize} bytes.");
                    }

                    $modifiers = '';
                    if (isset($req['flags']) && is_array($req['flags'])) {
                        foreach ($req['flags'] as $flag) {
                            if (in_array($flag, ['i', 'm', 's', 'x', 'A', 'D', 'U', 'u'])) {
                                $modifiers .= $flag;
                            }
                        }
                    }

                    // Ensure UTF-8 mode is explicitly set to safely calculate char boundaries
                    if (strpos($modifiers, 'u') === false) {
                        $modifiers .= 'u';
                    }

                    $pattern = '/' . str_replace('/', '\\/', $req['regex']) . '/' . $modifiers;

                    // Prevent ReDoS hangs with strict backtracking and recursion limits
                    ini_set('pcre.backtrack_limit', '1000000');
                    ini_set('pcre.recursion_limit', '100000');

                    error_clear_last();
                    $matchesArray = [];
                    $success = @preg_match_all($pattern, $req['text'], $matchesArray, PREG_OFFSET_CAPTURE | PREG_SET_ORDER);
                    $errorMsg = error_get_last();

                    if ($success === false) {
                        throw new \Exception($errorMsg ? $errorMsg['message'] : "Regex compilation or execution failed (possible backtracking limit reached).");
                    }

                    $matchItems = [];
                    $matchCount = 0;

                    foreach ($matchesArray as $matchId => $match) {
                        if ($matchCount >= $maxMatches) {
                            throw new \Exception("Exceeded maximum allowed matches ({$maxMatches}).");
                        }

                        $fullMatch = $match[0][0];
                        $byteStart = $match[0][1];

                        $charStart = mb_strlen(substr($req['text'], 0, $byteStart), 'UTF-8');
                        $charEnd = $charStart + mb_strlen($fullMatch, 'UTF-8');

                        $groups = [];
                        $groupIndex = 1;
                        $groupCount = 0;

                        while (isset($match[$groupIndex])) {
                            if ($groupCount >= $maxGroups) {
                                throw new \Exception("Exceeded maximum allowed groups per match ({$maxGroups}).");
                            }

                            if ($match[$groupIndex][1] !== -1) {
                                $gByteStart = $match[$groupIndex][1];
                                $gContent = $match[$groupIndex][0];
                                $gCharStart = mb_strlen(substr($req['text'], 0, $gByteStart), 'UTF-8');
                                $gCharEnd = $gCharStart + mb_strlen($gContent, 'UTF-8');

                                $groups[] = [
                                    'group_id' => $groupIndex,
                                    'name' => null,
                                    'content' => $gContent,
                                    'start' => $gCharStart,
                                    'end' => $gCharEnd
                                ];
                            }
                            $groupIndex++;
                            $groupCount++;
                        }

                        $matchItems[] = [
                            'match_id' => $matchId,
                            'full_match' => $fullMatch,
                            'start' => $charStart,
                            'end' => $charEnd,
                            'groups' => $groups
                        ];
                        $matchCount++;
                    }
                    $res['matches'] = $matchItems;

                } catch (\Exception $e) {
                    self::handleDlq($client, $req, $e->getMessage());
                    $res['success'] = false;
                    $res['error'] = $e->getMessage();
                }

                $res['execution_time_ms'] = (microtime(true) - $start) * 1000;

                $resJson = json_encode($res);
                if (strlen($resJson) > $maxJsonSize) {
                    $res['success'] = false;
                    $res['matches'] = [];
                    $res['error'] = "Output JSON exceeds maximum allowed size of {$maxJsonSize} bytes.";
                    $resJson = json_encode($res);
                }

                $client->setex("result:" . $req['task_id'], 60, $resJson);
                $client->publish("result:" . $req['task_id'], "ready");

            } catch (\Exception $e) {
                echo "[Error] PHP Worker loop failure: " . $e->getMessage() . "\n";
                // Disconnect to force Predis to re-establish the socket on the next iteration
                try {
                    $client->disconnect();
                } catch (\Exception $ex) {
                    // Ignore disconnect errors
                }
                // Sleep to avoid a rapid spin-loop if the Redis server is completely down
                sleep(2);
            }
        }
    }
}