package main

import (
	"fmt"
	"strings"
)

var goRegexFlagOrder = []string{"i", "m", "s", "U"}

type engineFlagMeta struct {
	description string
	group       string
}

var goRegexFlagMetadata = map[string]engineFlagMeta{
	"i": {description: "Case-insensitive matching.", group: "Basic"},
	"m": {description: "Multiline mode. Makes ^ and $ work per line.", group: "Basic"},
	"s": {description: "DotAll mode. Makes . match newline.", group: "Basic"},
	"U": {description: "Ungreedy mode where quantifiers are lazy by default.", group: "Advance"},
}

var goRegexSupportedFlags = map[string]struct{}{
	"i": {},
	"m": {},
	"s": {},
	"U": {},
}

func supportedGoRegexFlags() []EngineFlag {
	flags := make([]EngineFlag, 0, len(goRegexFlagOrder))
	for _, name := range goRegexFlagOrder {
		meta, ok := goRegexFlagMetadata[name]
		if !ok {
			meta = engineFlagMeta{
				description: fmt.Sprintf("Flag (%s)", name),
				group:       "Basic",
			}
		}
		flags = append(flags, EngineFlag{
			Name:        name,
			Description: meta.description,
			Group:       meta.group,
		})
	}
	return flags
}

func buildGoRegexInlineFlagPrefix(flags []string) (string, error) {
	if len(flags) == 0 {
		return "", nil
	}

	requested := make(map[string]struct{}, len(flags))
	for _, flag := range flags {
		if _, ok := goRegexSupportedFlags[flag]; !ok {
			return "", fmt.Errorf("unsupported regex flag for Go regexp: %q", flag)
		}
		requested[flag] = struct{}{}
	}

	var b strings.Builder
	for _, flag := range goRegexFlagOrder {
		if _, ok := requested[flag]; ok {
			b.WriteString(flag)
		}
	}

	if b.Len() == 0 {
		return "", nil
	}

	return "(?" + b.String() + ")", nil
}
