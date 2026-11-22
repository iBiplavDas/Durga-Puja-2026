// The app shell: what index.html asks for up front and what sw.js keeps for offline use.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';

const dir = new URL('../../app/', import.meta.url);
const read = (f) => readFileSync(new URL(f, dir), 'utf8');

/** Every module app.js loads through static imports (dynamic import() is left out on purpose). */
function staticGraph() {
  const seen = new Set(['app.js']), q = ['app.js'];
  while (q.length) {
    const f = q.shift();
    for (const m of read(f).matchAll(/^\s*import\s+(?:[^'"]*?from\s+)?['"](\.[^'"]+)['"]/gm)) {
      const r = path.posix.normalize(path.posix.join(path.posix.dirname(f), m[1]));
      if (!seen.has(r)) { seen.add(r); q.push(r); }
    }
  }
  return seen;
}

test('index.html modulepreloads exactly the modules app.js imports', () => {
  const pre = new Set([...read('index.html').matchAll(/<link rel="modulepreload" href="([^"]+)">/g)].map((m) => m[1]));
  assert.deepEqual([...pre].sort(), [...staticGraph()].sort());
});

test('Hindi strings are not part of the first load', () => {
  assert.ok(!staticGraph().has('i18n_hi.js'), 'i18n_hi.js should load through loadLang() only');
});

test('sw.js precaches every app module, so the app works offline', () => {
  const shell = new Set(read('sw.js').match(/const SHELL = \[([\s\S]*?)\];/)[1].match(/'([^']+)'/g).map((s) => s.slice(1, -1)));
  const modules = [...readdirSync(dir).filter((f) => f.endsWith('.js') && f !== 'sw.js'),
    ...readdirSync(new URL('views/', dir)).filter((f) => f.endsWith('.js')).map((f) => 'views/' + f)];
  assert.deepEqual(modules.filter((f) => !shell.has(f)), [], 'missing from SHELL in sw.js');
  for (const f of shell) assert.doesNotThrow(() => readFileSync(new URL(f === './' ? 'index.html' : f, dir)), `SHELL lists a missing file: ${f}`);
});
