import { WORKER_VERSION, WORKER_RELEASE_DATE } from './common.js';
import { engine as v8Standard } from './v8_standard.js';
import { engine as v8Re2 } from './v8_re2.js';

export const ENGINES = [
  v8Standard,
  v8Re2
];

export const WORKER_INFO = {
  worker_name: "worker-v8",
  worker_version: WORKER_VERSION,
  worker_release_date: WORKER_RELEASE_DATE,
  // Contract version: "1.1" = match offsets normalized to Unicode code points.
  worker_schema_version: "1.1",
  engines: ENGINES
};