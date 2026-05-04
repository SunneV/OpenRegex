package main

import (
	"context"
	"encoding/json"
	"fmt"
	"os"
	"runtime"

	"github.com/redis/go-redis/v9"
)

const (
	CAT_CLASSES     = "Character Classes & Escapes"
	CAT_ANCHORS     = "Anchors & Boundaries"
	CAT_QUANTIFIERS = "Quantifiers"
	CAT_GROUPS      = "Grouping & Backreferences"
	CAT_ADVANCED    = "Lookarounds & Advanced"
)

func registerEngines(ctx context.Context, client *redis.Client) error {
	workerVersion := os.Getenv("WORKER_VERSION")
	if workerVersion == "" {
		workerVersion = "Unknown"
	}
	workerReleaseDate := os.Getenv("WORKER_RELEASE_DATE")
	if workerReleaseDate == "" {
		workerReleaseDate = "Unreleased"
	}

	engineInfo := EngineInfo{
		EngineID:              "go_standard",
		EngineLanguageType:    "Go",
		EngineLanguageVersion: runtime.Version(),
		EngineRegexLib:        "regexp",
		EngineRegexLibVersion: runtime.Version(),
		EngineLabel:           "Go (regexp)",
		EngineCapabilities: EngineCapabilities{
			Flags:              supportedGoRegexFlags(),
			SupportsLookaround: false,
			SupportsBackrefs:   false,
		},
		EngineDocs: EngineDocs{
			Trivia: []string{
				"Based on the RE2 syntax and algorithms.",
				"Go's standard library (including regexp) is distributed under a BSD-3-Clause style Go license.",
				"Guarantees linear time O(n) execution, preventing ReDoS.",
				"Supports inline flags i, m, s, and U.",
				"Does not support backreferences or lookaround assertions.",
			},
			CheatSheetURL: "https://pkg.go.dev/regexp/syntax",
		},
		EngineCheatSheet: []CheatSheetCategory{
			{
				Category: CAT_CLASSES,
				Items: []CheatSheetItem{
					{Character: ".", Description: "Any character except newline unless the 's' flag is set"},
					{Character: "\\w", Description: "ASCII word character ([0-9A-Za-z_])"},
					{Character: "\\W", Description: "ASCII non-word character"},
					{Character: "\\d", Description: "ASCII digit ([0-9])"},
					{Character: "\\D", Description: "ASCII non-digit"},
					{Character: "\\s", Description: "ASCII whitespace ([\\t\\n\\f\\r ])"},
					{Character: "\\S", Description: "ASCII non-whitespace character"},
					{Character: "[a-z]", Description: "Character class (inclusive)"},
					{Character: "[^a-z]", Description: "Negated character class (exclusive)"},
					{Character: "\\p{Greek}", Description: "Unicode character class"},
					{Character: "\\P{Greek}", Description: "Negated Unicode character class"},
				},
			},
			{
				Category: CAT_ANCHORS,
				Items: []CheatSheetItem{
					{Character: "^", Description: "Start of text (or line if the 'm' flag is set)"},
					{Character: "$", Description: "End of text (or line if the 'm' flag is set)"},
					{Character: "\\A", Description: "Absolute start of text"},
					{Character: "\\z", Description: "Absolute end of text"},
					{Character: "\\b", Description: "ASCII word boundary"},
					{Character: "\\B", Description: "ASCII non-word boundary"},
				},
			},
			{
				Category: CAT_QUANTIFIERS,
				Items: []CheatSheetItem{
					{Character: "*", Description: "0 or more times (greedy unless the 'U' flag is set)"},
					{Character: "+", Description: "1 or more times (greedy unless the 'U' flag is set)"},
					{Character: "?", Description: "0 or 1 time (greedy unless the 'U' flag is set)"},
					{Character: "{m}", Description: "Exactly m times"},
					{Character: "{m,n}", Description: "Between m and n times (greedy unless the 'U' flag is set)"},
					{Character: "*?", Description: "0 or more times (lazy unless the 'U' flag is set)"},
					{Character: "+?", Description: "1 or more times (lazy unless the 'U' flag is set)"},
					{Character: "??", Description: "0 or 1 time (lazy unless the 'U' flag is set)"},
					{Character: "{m,n}?", Description: "Between m and n times (lazy unless the 'U' flag is set)"},
				},
			},
			{
				Category: CAT_GROUPS,
				Items: []CheatSheetItem{
					{Character: "(...)", Description: "Capturing group"},
					{Character: "(?:...)", Description: "Non-capturing group"},
					{Character: "x|y", Description: "Alternation (match x or y)"},
					{Character: "(?P<name>...)", Description: "Named capturing group"},
					{Character: "(?<name>...)", Description: "Named capturing group"},
				},
			},
			{
				Category: CAT_ADVANCED,
				Items: []CheatSheetItem{
					{Character: "(?i)", Description: "Inline flag: case-insensitive matching"},
					{Character: "(?m)", Description: "Inline flag: multiline mode; ^ and $ match line boundaries"},
					{Character: "(?s)", Description: "Inline flag: dotall mode; . matches newline"},
					{Character: "(?U)", Description: "Inline flag: ungreedy mode; swaps greedy and lazy quantifiers"},
					{Character: "(?i:...)", Description: "Scoped inline flag group"},
					{Character: "(?-i:...)", Description: "Scoped inline flag clearing group"},
				},
			},
		},
		EngineExamples: []EngineExample{
			{
				Regex: "(?P<IP>(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d))(/(\\d{1,2}))?(?:-(?P<IP2>(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)))?(:(?P<port>\\d{1,5}))?",
				Text:  "This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255\n192.168.1.1-192.168.1.255:80\n192.168.1.0/24:80",
			},
		},
	}

	workerInfo := WorkerInfo{
		WorkerName:        "worker-go",
		WorkerVersion:     workerVersion,
		WorkerReleaseDate: workerReleaseDate,
		Engines:           []EngineInfo{engineInfo},
	}

	jsonBytes, err := json.Marshal(workerInfo)
	if err != nil {
		return err
	}

	err = client.HSet(ctx, "openregex:workers", workerInfo.WorkerName, string(jsonBytes)).Err()
	if err == nil {
		fmt.Printf("[Discovery] Registered '%s' with %d engines.\n", workerInfo.WorkerName, len(workerInfo.Engines))
	}
	return err
}
