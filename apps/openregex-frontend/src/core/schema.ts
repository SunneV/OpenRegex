// Version of the worker communication contract this frontend expects.
// Workers report theirs via `worker_schema_version` in /api/engines.
// "1.0" (or missing) = legacy contract with engine-native match offsets;
// "1.1" = match offsets normalized to Unicode code points.
export const SUPPORTED_WORKER_SCHEMA_VERSION = '1.1';

export const getWorkerSchemaVersion = (v?: string): string => v || '1.0';

export const isWorkerSchemaSupported = (v?: string): boolean =>
  getWorkerSchemaVersion(v) === SUPPORTED_WORKER_SCHEMA_VERSION;
