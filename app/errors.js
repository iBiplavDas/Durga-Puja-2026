/* Error beacon: so the team sees breakage on festival nights before users report it.
 * Uncaught errors and unhandled promise rejections go to the log_client_error RPC
 * (supabase/migrations/*_client_errors.sql) as one small record each: the message (cut to 300
 * characters, with e-mails, long numbers and token-like strings masked), the file and line (no query
 * string), the data version, the browser family and major version (never the full user-agent), and
 * the screen. No device id, account, name or location. Each distinct error is sent once per page
 * load, at most 10 in all, and noise (ResizeObserver, browser extensions, cross-origin "Script
 * error.") is dropped. If the backend isn't set up, or doesn't have the RPC yet (404), it goes quiet.
 * The beacon never throws. Imported first from app.js, so it is listening before the rest loads. */
import { CONFIG } from './config.js';

export const MAX_PER_LOAD = 10;
const EXT = /^(chrome|moz|safari|safari-web|ms-browser)-extension:\/\//i;
const NOISE = [/ResizeObserver loop/i, /^Script error\.?$/i];

/** Keep only the path of a script URL: no query string or hash, and no origin when it's ours. */
export function cleanSource(src, origin = '') {
  if (!src) return '';
  let s = String(src).split(/[?#]/)[0];
  if (origin && s.startsWith(origin)) s = s.slice(origin.length) || '/';
  return s.slice(0, 200);
}

/** Mask anything that could identify someone or leak a secret, then cut to `max` characters. */
export function scrub(msg, max = 300) {
  return String(msg ?? '')
    .replace(/https?:\/\/[^\s?#'"]+[?#][^\s'"]*/g, (u) => u.split(/[?#]/)[0])   // query strings in URLs
    .replace(/[\w.+-]+@[\w-]+\.[\w.-]+/g, '<email>')
    .replace(/[A-Za-z0-9_-]{32,}/g, '<token>')
    .replace(/\+?\d[\d\s-]{6,}\d/g, '<number>')                                   // phone numbers and the like
    .replace(/\s+/g, ' ').trim().slice(0, max);
}

/** First frame of a stack trace: { source, line, col }, or null. Handles V8 and Safari/Firefox styles. */
export function frameFromStack(stack) {
  const m = /(?:\(|@|\bat )((?:https?|blob|file|[a-z-]+-extension):\/\/[^\s)]+?):(\d+):(\d+)/i.exec(String(stack || ''));
  return m ? { source: m[1], line: +m[2], col: +m[3] } : null;
}

/** "Chrome 130 Android", "Safari 17 iOS", "Samsung 25 Android", "Instagram iOS"… never the full UA. */
export function uaFamily(ua = '') {
  const os = /Android/i.test(ua) ? 'Android' : /iPhone|iPad|iPod/i.test(ua) ? 'iOS' : /Windows/i.test(ua) ? 'Windows'
    : /Mac OS X|Macintosh/i.test(ua) ? 'macOS' : /CrOS/i.test(ua) ? 'ChromeOS' : /Linux/i.test(ua) ? 'Linux' : '';
  const v = (re) => (re.exec(ua) || [])[1]?.split('.')[0] || '';
  const browsers = [
    [/Instagram/, 'Instagram', null], [/FBAN|FBAV/, 'Facebook', null], [/WhatsApp/i, 'WhatsApp', null],
    [/SamsungBrowser/, 'Samsung', /SamsungBrowser\/([\d.]+)/], [/EdgA?\//, 'Edge', /EdgA?\/([\d.]+)/],
    [/OPR\/|Opera/, 'Opera', /OPR\/([\d.]+)/], [/UCBrowser/, 'UC', /UCBrowser\/([\d.]+)/],
    [/Firefox\/|FxiOS/, 'Firefox', /(?:Firefox|FxiOS)\/([\d.]+)/], [/CriOS/, 'Chrome', /CriOS\/([\d.]+)/],
    [/Chrome\//, 'Chrome', /Chrome\/([\d.]+)/], [/Safari\//, 'Safari', /Version\/([\d.]+)/],
  ];
  const hit = browsers.find(([re]) => re.test(ua));
  const name = hit ? [hit[1], hit[2] ? v(hit[2]) : ''].filter(Boolean).join(' ') : 'Other';
  return [name, os].filter(Boolean).join(' ').slice(0, 40);
}

/** Turn an error or rejection event into a record, or null when it's noise we don't want. */
export function toRecord(ev, { origin = '', kind = 'error' } = {}) {
  let message, source, line = null, col = null;
  if (kind === 'rejection') {
    const r = ev?.reason;
    message = r instanceof Error || (r && typeof r === 'object' && 'message' in r) ? `${r.name || 'Error'}: ${r.message}` : String(r);
    const f = frameFromStack(r?.stack);
    if (f) ({ source, line, col } = f);
  } else {
    message = ev?.message || (ev?.error ? `${ev.error.name || 'Error'}: ${ev.error.message}` : '');
    source = ev?.filename; line = ev?.lineno ?? null; col = ev?.colno ?? null;
    if (!source) { const f = frameFromStack(ev?.error?.stack); if (f) ({ source, line, col } = f); }
  }
  if (!message && !source) return null;
  if (source && EXT.test(source)) return null;
  if (EXT.test(String(ev?.error?.stack || ev?.reason?.stack || ''))) return null;
  if (NOISE[0].test(message || '')) return null;
  if (NOISE[1].test(String(message || '').trim()) && !source) return null;
  return { kind, message: scrub(message), source: cleanSource(source, origin), line: line || null, col: col || null };
}

/** Dedupe (same message + source once per load) and cap. Returns report(record) → true if it was sent. */
export function createBeacon(send, max = MAX_PER_LOAD) {
  const seen = new Set();
  let sent = 0;
  return (rec) => {
    if (!rec || sent >= max) return false;
    const key = rec.message + '|' + rec.source;
    if (seen.has(key)) return false;
    seen.add(key); sent++;
    try { send(rec); } catch { /* never throw from the beacon */ }
    return true;
  };
}

/* ---------------------------------------------------------------- browser wiring */
let view = 'home';
const context = () => {
  let version = '';
  try { version = JSON.parse(localStorage.getItem('pp:dataVersion') || '""') || ''; } catch { /* private mode */ }
  const sheet = typeof document !== 'undefined' && document.querySelector?.('#sheet.open') ? ':sheet' : '';
  return { version: String(version).slice(0, 40), view: (view + sheet).slice(0, 20), page: location.pathname.slice(0, 100) };
};

function install() {
  const cfg = CONFIG.community || {};
  const url = (cfg.url || '').replace(/\/+$/, ''), key = cfg.anonKey || '';
  if (!url || !key) return;
  let off = false;
  try { off = sessionStorage.getItem('pp:errbeacon') === 'off'; } catch { /* ignore */ }
  const browser = uaFamily(navigator.userAgent || '');
  const report = createBeacon((rec) => {
    if (off) return;
    const c = context();
    fetch(`${url}/rest/v1/rpc/log_client_error`, {
      method: 'POST', keepalive: true, headers: { apikey: key, 'Content-Type': 'application/json' },
      body: JSON.stringify({ p_message: rec.message, p_source: rec.source, p_line: rec.line, p_col: rec.col,
        p_kind: rec.kind, p_version: c.version, p_browser: browser, p_view: c.view, p_page: c.page }),
    }).then((r) => {
      if (r.status === 404) { off = true; try { sessionStorage.setItem('pp:errbeacon', 'off'); } catch { /* ignore */ } }
    }).catch(() => {});
  });
  const origin = location.origin;
  addEventListener('error', (e) => {
    try { if (e instanceof ErrorEvent) report(toRecord(e, { origin })); } catch { /* ignore */ }   // not resource-load errors
  });
  addEventListener('unhandledrejection', (e) => { try { report(toRecord(e, { origin, kind: 'rejection' })); } catch { /* ignore */ } });
  addEventListener('viewchange', (e) => { view = String(e.detail || view); });
}

if (typeof window !== 'undefined' && typeof addEventListener === 'function') {
  try { view = (location.hash.slice(1).match(/^[a-z]+/) || ['home'])[0]; install(); } catch { /* never break the app */ }
}
