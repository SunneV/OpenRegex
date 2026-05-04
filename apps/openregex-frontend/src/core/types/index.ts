export interface CheatSheetItem {
  character: string;
  description: string;
}

export interface CheatSheetCategory {
  category: string;
  items: CheatSheetItem[];
}

export interface EngineDocs {
  trivia: string[];
  cheat_sheet_url?: string;
}

export interface EngineFlag {
  name: string;
  description: string;
  group: string;
}

export interface EngineCapabilities {
  flags: EngineFlag[];
  supports_lookaround: boolean;
  supports_backrefs: boolean;
}

export interface EngineExample {
  regex: string;
  text: string;
}

export interface EngineInfo {
  engine_id: string;
  engine_language_type: string;
  engine_language_version: string;
  engine_regex_lib: string;
  engine_regex_lib_version: string;
  engine_label: string;
  engine_capabilities: EngineCapabilities;
  engine_docs: EngineDocs;
  engine_cheat_sheet: CheatSheetCategory[];
  engine_examples: EngineExample[];
}

export interface WorkerInfo {
  worker_name: string;
  worker_version: string;
  worker_release_date: string;
  engines: EngineInfo[];
}

export interface MatchGroup {
  group_id: number;
  name: string | null;
  content: string;
  start: number;
  end: number;
}

export interface MatchItem {
  match_id: number;
  full_match: string;
  start: number;
  end: number;
  groups: MatchGroup[];
}

export interface ASTNode {
  type: 'root' | 'text' | 'group';
  text?: string;
  isCapturing?: boolean;
  id?: number;
  children?: ASTNode[];
  startIndex?: number;
  endIndex?: number;
}
