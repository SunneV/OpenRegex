package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"regexp"
	"strconv"
	"sync"
	"time"
	"unicode/utf8"

	"github.com/redis/go-redis/v9"
)

type RegexCache struct {
	sync.RWMutex
	m    map[string]*regexp.Regexp
	keys []string
}

func (c *RegexCache) Get(key string) *regexp.Regexp {
	c.RLock()
	defer c.RUnlock()
	return c.m[key]
}

func (c *RegexCache) Set(key string, r *regexp.Regexp) {
	c.Lock()
	defer c.Unlock()
	if _, exists := c.m[key]; !exists {
		c.keys = append(c.keys, key)
		if len(c.keys) > 1000 {
			delete(c.m, c.keys[0])
			c.keys = c.keys[1:]
		}
	}
	c.m[key] = r
}

var regexCache = &RegexCache{m: make(map[string]*regexp.Regexp)}

// buildByteToCharMap returns a prefix map converting UTF-8 byte offsets to
// Unicode code point indices, or nil for pure-ASCII text where both are equal.
// Go's regexp reports byte offsets; the platform contract requires code points.
func buildByteToCharMap(text string) []int {
	ascii := true
	for i := 0; i < len(text); i++ {
		if text[i] >= 0x80 {
			ascii = false
			break
		}
	}
	if ascii {
		return nil
	}

	m := make([]int, len(text)+1)
	count := 0
	for i, r := range text {
		width := utf8.RuneLen(r)
		if width < 1 {
			width = 1
		}
		for b := i; b < i+width; b++ {
			m[b] = count
		}
		count++
	}
	m[len(text)] = count
	return m
}

func toCharIndex(m []int, byteIdx int) int {
	if m == nil {
		return byteIdx
	}
	if byteIdx >= len(m) {
		byteIdx = len(m) - 1
	}
	return m[byteIdx]
}

func getEnvInt(key string, fallback int) int {
	if val, ok := os.LookupEnv(key); ok {
		if i, err := strconv.Atoi(val); err == nil {
			return i
		}
	}
	return fallback
}

func handleDlq(ctx context.Context, client *redis.Client, taskJson string, errorMsg string) {
	var taskMap map[string]interface{}
	if err := json.Unmarshal([]byte(taskJson), &taskMap); err == nil {
		attemptCount := 0.0
		if val, ok := taskMap["attempt_count"].(float64); ok {
			attemptCount = val
		}
		taskMap["attempt_count"] = attemptCount + 1
		taskMap["error_reason"] = errorMsg

		if modifiedJson, err := json.Marshal(taskMap); err == nil {
			client.LPush(ctx, "queue:go:dead", string(modifiedJson))
		}
	}
}

func listenAndProcess(client *redis.Client) {
	fmt.Println("[Worker] Go worker listening on 'queue:go'...")
	bgCtx := context.Background()

	timeoutMs := getEnvInt("WORKER_EXECUTION_TIMEOUT_MS", 1000)
	maxInputSize := getEnvInt("WORKER_MAX_INPUT_SIZE", 10485760)
	maxMatches := getEnvInt("WORKER_MAX_MATCHES", 10000)
	maxGroups := getEnvInt("WORKER_MAX_GROUPS", 1000)
	maxJsonSize := getEnvInt("WORKER_MAX_JSON_SIZE", 10485760)

	for {
		result, err := client.BRPop(bgCtx, 0, "queue:go").Result()
		if err != nil {
			time.Sleep(100 * time.Millisecond)
			continue
		}

		go func(taskJson string) {
			var req MatchRequest
			if err := json.Unmarshal([]byte(taskJson), &req); err != nil {
				handleDlq(bgCtx, client, taskJson, fmt.Sprintf("JSON parse error: %v", err))
				return
			}

			// CLAIM-CHECK: Extract text_payload_id dynamically
			var claimCheck struct {
				TextPayloadID *string `json:"text_payload_id"`
			}
			_ = json.Unmarshal([]byte(taskJson), &claimCheck)

			if claimCheck.TextPayloadID != nil && *claimCheck.TextPayloadID != "" {
				payload, err := client.Get(bgCtx, *claimCheck.TextPayloadID).Result()
				if err != nil {
					errStr := "Payload expired or missing from Redis"
					handleDlq(bgCtx, client, taskJson, errStr)

					res := MatchResult{
						TaskID:          req.TaskID,
						EngineID:        req.EngineID,
						Success:         false,
						Matches:         []MatchItem{},
						ExecutionTimeMs: 0.0,
						Error:           &errStr,
					}
					resJson, _ := json.Marshal(res)
					client.SetEx(bgCtx, "result:"+req.TaskID, string(resJson), 60*time.Second)
					client.Publish(bgCtx, "result:"+req.TaskID, "ready")
					return
				}
				req.Text = payload
			}

			start := time.Now()
			ctx, cancel := context.WithTimeout(context.Background(), time.Duration(timeoutMs)*time.Millisecond)
			defer cancel()

			resultChan := make(chan MatchResult, 1)

			go func() {
				res := MatchResult{
					TaskID:   req.TaskID,
					EngineID: req.EngineID,
				}

				if len(req.Text) > maxInputSize {
					execTime := float64(time.Since(start).Microseconds()) / 1000.0
					errStr := fmt.Sprintf("Input text exceeds maximum allowed size of %d bytes.", maxInputSize)
					res.Success = false
					res.Matches = []MatchItem{}
					res.ExecutionTimeMs = execTime
					res.Error = &errStr
					resultChan <- res
					return
				}

				inlineFlagPrefix, flagErr := buildGoRegexInlineFlagPrefix(req.Flags)
				if flagErr != nil {
					execTime := float64(time.Since(start).Microseconds()) / 1000.0
					errStr := flagErr.Error()
					res.Success = false
					res.Matches = []MatchItem{}
					res.ExecutionTimeMs = execTime
					res.Error = &errStr
					resultChan <- res
					return
				}

				fullRegex := inlineFlagPrefix + req.Regex

				re := regexCache.Get(fullRegex)
				if re == nil {
					var err error
					re, err = regexp.Compile(fullRegex)
					if err != nil {
						execTime := float64(time.Since(start).Microseconds()) / 1000.0
						errStr := err.Error()
						res.Success = false
						res.Matches = []MatchItem{}
						res.ExecutionTimeMs = execTime
						res.Error = &errStr
						resultChan <- res
						return
					}
					regexCache.Set(fullRegex, re)
				}

				submatches := re.FindAllStringSubmatchIndex(req.Text, maxMatches+1)
				names := re.SubexpNames()
				byteToChar := buildByteToCharMap(req.Text)

				var matchItems []MatchItem

				for matchId, matchIdxs := range submatches {
					if matchId >= maxMatches {
						execTime := float64(time.Since(start).Microseconds()) / 1000.0
						errStr := fmt.Sprintf("Exceeded maximum allowed matches (%d).", maxMatches)
						res.Success = false
						res.Matches = []MatchItem{}
						res.ExecutionTimeMs = execTime
						res.Error = &errStr
						resultChan <- res
						return
					}

					var groups []MatchGroup
					fullMatch := req.Text[matchIdxs[0]:matchIdxs[1]]

					for i := 1; i < len(matchIdxs)/2; i++ {
						if len(groups) >= maxGroups {
							execTime := float64(time.Since(start).Microseconds()) / 1000.0
							errStr := fmt.Sprintf("Exceeded maximum allowed groups per match (%d).", maxGroups)
							res.Success = false
							res.Matches = []MatchItem{}
							res.ExecutionTimeMs = execTime
							res.Error = &errStr
							resultChan <- res
							return
						}

						groupStart := matchIdxs[2*i]
						groupEnd := matchIdxs[2*i+1]

						if groupStart != -1 && groupEnd != -1 {
							var namePtr *string
							if i < len(names) && names[i] != "" {
								n := names[i]
								namePtr = &n
							}

							groups = append(groups, MatchGroup{
								GroupID: i,
								Name:    namePtr,
								Content: req.Text[groupStart:groupEnd],
								Start:   toCharIndex(byteToChar, groupStart),
								End:     toCharIndex(byteToChar, groupEnd),
							})
						}
					}

					if groups == nil {
						groups = []MatchGroup{}
					}

					matchItems = append(matchItems, MatchItem{
						MatchID:   matchId,
						FullMatch: fullMatch,
						Start:     toCharIndex(byteToChar, matchIdxs[0]),
						End:       toCharIndex(byteToChar, matchIdxs[1]),
						Groups:    groups,
					})
				}

				if matchItems == nil {
					matchItems = []MatchItem{}
				}

				execTime := float64(time.Since(start).Microseconds()) / 1000.0
				res.Success = true
				res.Matches = matchItems
				res.ExecutionTimeMs = execTime
				resultChan <- res
			}()

			var finalRes MatchResult
			select {
			case finalRes = <-resultChan:
				// Execution completed
			case <-ctx.Done():
				// SLA Timeout
				handleDlq(bgCtx, client, taskJson, "TIMEOUT: Go execution exceeded SLA.")
				execTime := float64(time.Since(start).Microseconds()) / 1000.0
				errStr := fmt.Sprintf("TIMEOUT: Go execution exceeded %dms SLA.", timeoutMs)
				finalRes = MatchResult{
					TaskID:          req.TaskID,
					EngineID:        req.EngineID,
					Success:         false,
					Matches:         []MatchItem{},
					ExecutionTimeMs: execTime,
					Error:           &errStr,
				}
			}

			resJson, _ := json.Marshal(finalRes)

			if len(resJson) > maxJsonSize {
				errStr := fmt.Sprintf("Output JSON exceeds maximum allowed size of %d bytes.", maxJsonSize)
				finalRes = MatchResult{
					TaskID:          req.TaskID,
					EngineID:        req.EngineID,
					Success:         false,
					Matches:         []MatchItem{},
					ExecutionTimeMs: finalRes.ExecutionTimeMs,
					Error:           &errStr,
				}
				resJson, _ = json.Marshal(finalRes)
			}

			client.SetEx(bgCtx, "result:"+req.TaskID, string(resJson), 60*time.Second)
			client.Publish(bgCtx, "result:"+req.TaskID, "ready")

		}(result[1])
	}
}