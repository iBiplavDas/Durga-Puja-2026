import { test } from 'node:test';
import assert from 'node:assert/strict';
import { toRecord, createBeacon, cleanSource, scrub, uaFamily, frameFromStack, MAX_PER_LOAD } from '../../app/errors.js';

const O = 'https://pujoparikramaguide.in';

test('error events become compact records with a clean source', () => {
  const r = toRecord({ message: 'TypeError: x is undefined', filename: `${O}/app.js?v=3#x`, lineno: 12, colno: 7 }, { origin: O });
  assert.deepEqual(r, { kind: 'error', message: 'TypeError: x is undefined', source: '/app.js', line: 12, col: 7 });
  assert.equal(cleanSource('https://cdn.example.com/lib.js?x=1'), 'https://cdn.example.com/lib.js');
  assert.equal(cleanSource(''), '');
});

test('rejections take the message and the first stack frame', () => {
  const err = new Error('boom');
  err.stack = `Error: boom\n    at load (${O}/views/home.js?v=2:41:9)\n    at ${O}/app.js:3:1`;
  const r = toRecord({ reason: err }, { origin: O, kind: 'rejection' });
  assert.deepEqual(r, { kind: 'rejection', message: 'Error: boom', source: '/views/home.js', line: 41, col: 9 });
  assert.equal(toRecord({ reason: 'plain string' }, { kind: 'rejection' }).message, 'plain string');
  assert.deepEqual(frameFromStack(`render@${O}/ui.js:10:2`), { source: `${O}/ui.js`, line: 10, col: 2 });
  assert.equal(frameFromStack('no frames here'), null);
});

test('noise is ignored', () => {
  assert.equal(toRecord({ message: 'ResizeObserver loop completed with undelivered notifications.' }), null);
  assert.equal(toRecord({ message: 'Script error.' }), null);
  assert.equal(toRecord({ message: 'Script error', filename: '' }), null);
  assert.equal(toRecord({ message: 'x', filename: 'chrome-extension://abc/content.js' }), null);
  assert.equal(toRecord({ message: 'x', filename: 'moz-extension://abc/content.js' }), null);
  const ext = new Error('ext'); ext.stack = 'Error: ext\n at chrome-extension://abc/inject.js:1:1';
  assert.equal(toRecord({ reason: ext }, { kind: 'rejection' }), null);
  assert.equal(toRecord({}), null);
  assert.notEqual(toRecord({ message: 'Script error.', filename: `${O}/app.js` }, { origin: O }), null, 'with a source it is real');
});

test('messages are truncated and masked', () => {
  assert.equal(scrub('x'.repeat(500)).length <= 300, true);
  const m = scrub('Call +91 98300 12345, mail a.b@example.com, see https://x.org/p?token=abc and eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9abcdef');
  assert.ok(!/98300|example\.com|token=abc|eyJhbGci/.test(m), m);
  assert.ok(m.includes('<number>') && m.includes('<email>') && m.includes('https://x.org/p') && m.includes('<token>'), m);
});

test('each error is sent once per page load, at most ten in all, and the beacon never throws', () => {
  const sent = [];
  const report = createBeacon((r) => sent.push(r));
  const rec = (i) => ({ kind: 'error', message: 'm' + i, source: '/app.js', line: 1, col: 1 });
  assert.equal(report(rec(0)), true);
  assert.equal(report(rec(0)), false, 'same message and source: once');
  assert.equal(report({ ...rec(0), source: '/ui.js' }), true, 'same message, another file: separate');
  for (let i = 1; i < 20; i++) report(rec(i));
  assert.equal(sent.length, MAX_PER_LOAD);
  assert.equal(report(null), false);
  const boom = createBeacon(() => { throw new Error('network'); });
  assert.doesNotThrow(() => boom(rec(1)));
});

test('browser family, never the full user agent', () => {
  const ua = {
    'Chrome 130 Android': 'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.58 Mobile Safari/537.36',
    'Safari 17 iOS': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
    'Samsung 25 Android': 'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/25.0 Chrome/121.0.0.0 Mobile Safari/537.36',
    'Instagram iOS': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 345.0.0',
    'Chrome 129 iOS': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/129.0.6668.69 Mobile/15E148 Safari/604.1',
    'Firefox 131 Windows': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
  };
  for (const [want, s] of Object.entries(ua)) assert.equal(uaFamily(s), want);
  assert.equal(uaFamily(''), 'Other');
});
