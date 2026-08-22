import { PersonalItem } from '../../../core/store/useStorageStore';

export const PERSONAL_DUMP_TYPE = 'openregex-personal-dump';
export const PERSONAL_DUMP_SCHEMA = 1;

export interface PersonalDump {
  type: typeof PERSONAL_DUMP_TYPE;
  schema: number;
  exported_at: string;
  items: PersonalItem[];
}

export function downloadPersonalDump(items: PersonalItem[]): void {
  const dump: PersonalDump = {
    type: PERSONAL_DUMP_TYPE,
    schema: PERSONAL_DUMP_SCHEMA,
    exported_at: new Date().toISOString(),
    items,
  };

  const blob = new Blob([JSON.stringify(dump, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `openregex-personal-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

const sanitizeItem = (raw: any): PersonalItem | null => {
  if (!raw || typeof raw !== 'object') return null;
  if (typeof raw.regex !== 'string' || typeof raw.engineId !== 'string') return null;
  return {
    id: typeof raw.id === 'string' && raw.id ? raw.id : crypto.randomUUID(),
    name: typeof raw.name === 'string' ? raw.name : undefined,
    tags: Array.isArray(raw.tags) ? raw.tags.filter((t: unknown) => typeof t === 'string') : [],
    engineId: raw.engineId,
    engineLabel: typeof raw.engineLabel === 'string' ? raw.engineLabel : raw.engineId,
    regex: raw.regex,
    text: typeof raw.text === 'string' ? raw.text : '',
    flags: Array.isArray(raw.flags) ? raw.flags.filter((f: unknown) => typeof f === 'string') : [],
    matchCount: typeof raw.matchCount === 'number' ? raw.matchCount : 0,
    timestamp: typeof raw.timestamp === 'number' ? raw.timestamp : Date.now(),
  };
};

/** Accepts a full dump envelope or a bare item array. Throws on unusable input. */
export function parsePersonalDump(rawJson: string): PersonalItem[] {
  let parsed: unknown;
  try {
    parsed = JSON.parse(rawJson);
  } catch {
    throw new Error('File is not valid JSON.');
  }

  const rawItems = Array.isArray(parsed)
    ? parsed
    : (parsed as any)?.type === PERSONAL_DUMP_TYPE && Array.isArray((parsed as any).items)
      ? (parsed as any).items
      : null;

  if (!rawItems) throw new Error('File is not an OpenRegex personal dump.');

  const items = rawItems.map(sanitizeItem).filter((i: PersonalItem | null): i is PersonalItem => i !== null);
  if (items.length === 0 && rawItems.length > 0) throw new Error('No valid items found in the dump.');
  return items;
}
