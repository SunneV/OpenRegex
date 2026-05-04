export const WORKER_VERSION = process.env.WORKER_VERSION || "1.0.0";
export const WORKER_RELEASE_DATE = process.env.WORKER_RELEASE_DATE || "Unreleased";
export const LANGUAGE_VERSION = process.version || "unknown";
export const V8_VERSION = process.versions.v8 || "unknown";

export const CAT_CLASSES = "Character Classes & Escapes";
export const CAT_ANCHORS = "Anchors & Boundaries";
export const CAT_QUANTIFIERS = "Quantifiers";
export const CAT_GROUPS = "Grouping & Backreferences";
export const CAT_ADVANCED = "Lookarounds & Advanced";

const FLAG_METADATA = {
  d: { description: "Return match indices when supported by the engine.", group: "Advance" },
  g: { description: "Global matching; find all matches and advance lastIndex.", group: "Basic" },
  i: { description: "Case-insensitive matching.", group: "Basic" },
  m: { description: "Multiline mode. Makes ^ and $ work per line.", group: "Basic" },
  s: { description: "DotAll mode. Makes . match newline.", group: "Basic" },
  u: { description: "Unicode-aware mode.", group: "Basic" },
  v: { description: "Unicode sets mode with set operations and string properties.", group: "Advance" },
  y: { description: "Sticky matching at lastIndex.", group: "Advance" },
};

export function buildEngineFlags(...flagNames) {
  return flagNames.map(name => {
    const meta = FLAG_METADATA[name] || { description: `Flag (${name})`, group: "Basic" };
    return {
      name,
      description: meta.description,
      group: meta.group
    };
  });
}
