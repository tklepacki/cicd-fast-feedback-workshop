/**
 * Writes the API contract to a file without starting the server.
 *
 * Used in CI: the spec is generated for the base branch and for the pull request, then the
 * two are compared with `oasdiff`. If the spec could only be fetched from a running
 * application, the contract check would stop being cheap - and its entire value lies in
 * costing a dozen seconds and running in parallel with the other fast checks.
 *
 * Usage: node scripts/dump-openapi.mjs [output-file]
 */
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { openapiDocument } from '../dist/server/server/openapi.js';

const target = process.argv[2] ?? 'openapi.json';

await mkdir(path.dirname(path.resolve(target)), { recursive: true });
await writeFile(target, `${JSON.stringify(openapiDocument, null, 2)}\n`, 'utf8');

console.log(`API contract written to ${target}`);
