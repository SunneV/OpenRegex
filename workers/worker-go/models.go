package main

type CheatSheetItem struct {
	Character   string `json:"character"`
	Description string `json:"description"`
}

type CheatSheetCategory struct {
	Category string           `json:"category"`
	Items    []CheatSheetItem `json:"items"`
}

type EngineDocs struct {
	Trivia        []string `json:"trivia"`
	CheatSheetURL string   `json:"cheat_sheet_url"`
}

type EngineFlag struct {
	Name        string `json:"name"`
	Description string `json:"description"`
	Group       string `json:"group"`
}

type EngineCapabilities struct {
	Flags              []EngineFlag `json:"flags"`
	SupportsLookaround bool     `json:"supports_lookaround"`
	SupportsBackrefs   bool     `json:"supports_backrefs"`
}

type EngineExample struct {
	Regex string `json:"regex"`
	Text  string `json:"text"`
}

type EngineInfo struct {
	EngineID              string               `json:"engine_id"`
	EngineLanguageType    string               `json:"engine_language_type"`
	EngineLanguageVersion string               `json:"engine_language_version"`
	EngineRegexLib        string               `json:"engine_regex_lib"`
	EngineRegexLibVersion string               `json:"engine_regex_lib_version"`
	EngineLabel           string               `json:"engine_label"`
	EngineCapabilities    EngineCapabilities   `json:"engine_capabilities"`
	EngineDocs            EngineDocs           `json:"engine_docs"`
	EngineCheatSheet      []CheatSheetCategory `json:"engine_cheat_sheet"`
	EngineExamples        []EngineExample      `json:"engine_examples"`
}

type WorkerInfo struct {
	WorkerName        string       `json:"worker_name"`
	WorkerVersion     string       `json:"worker_version"`
	WorkerReleaseDate string       `json:"worker_release_date"`
	Engines           []EngineInfo `json:"engines"`
}

type MatchRequest struct {
	TaskID   string   `json:"task_id"`
	EngineID string   `json:"engine_id"`
	Regex    string   `json:"regex"`
	Text     string   `json:"text"`
	Flags    []string `json:"flags"`
}

type MatchGroup struct {
	GroupID int     `json:"group_id"`
	Name    *string `json:"name"`
	Content string  `json:"content"`
	Start   int     `json:"start"`
	End     int     `json:"end"`
}

type MatchItem struct {
	MatchID   int          `json:"match_id"`
	FullMatch string       `json:"full_match"`
	Start     int          `json:"start"`
	End       int          `json:"end"`
	Groups    []MatchGroup `json:"groups"`
}

type MatchResult struct {
	TaskID          string      `json:"task_id"`
	EngineID        string      `json:"engine_id"`
	Success         bool        `json:"success"`
	Matches         []MatchItem `json:"matches"`
	ExecutionTimeMs float64     `json:"execution_time_ms"`
	Error           *string     `json:"error"`
}
