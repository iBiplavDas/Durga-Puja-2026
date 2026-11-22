# Speed and accessibility pass (November 2026)

Two items from the roadmap, done together: make the app open faster on a crowded, slow phone network, and make it
work for people who use a screen reader, a keyboard, large text or dark mode. Nothing was removed and the data didn't
change.

## How it was measured

* **Speed:** Playwright on an iPhone 13-sized page, cold cache, service worker off, network throttled through Chrome
  DevTools. *Slow 3G* = 400 ms round trip, 400 kbit/s. *Fast 3G* = 150 ms, 1.6 Mbit/s. Median of three runs.
  Wikimedia photos, YouTube and Supabase were blocked so runs compare like for like (they load after Home anyway).
  "Home shown" means the banner and the Home cards are on screen; "first paint" is the header alone.
* The live site is GitHub Pages, which gzips and speaks HTTP/2, so the main table uses a local server that does the
  same. `npm run serve` (Python, no gzip, HTTP/1.1) is shown too; it is much slower than the real site.
* **Accessibility:** axe-core 4 on Home, Explore, Routes, My Pujo, Moments, an open pandal page and the SOS page, in
  light and dark, against the e2e fake Supabase. Tap targets were listed with a small script (anything under 44 px).

## What loads on first open

| | Raw | Gzipped |
|---|---|---|
| `data/guide.json` | 690 KB | 97 KB |
| JavaScript before (35 modules, incl. Hindi strings) | 478 KB | 160 KB |
| JavaScript after (34 modules; Hindi loads only when chosen) | 406 KB | 142 KB |
| `styles.css` | 104 KB | 21 KB |
| Fonts (Inter, Fraunces, Tiro Bangla, Hind Siliguri 600) | 236 KB | (already compressed) |
| Banner photo `hero-1.jpg` / `hero-1-sm.jpg` | 287 KB / 61 KB | |
| Header dhak photo before / after | 54 KB / 5 KB | |

**The problem was the order, not the size.** The guide only started downloading after every module had loaded, one
import level at a time (app.js → state.js → i18n.js → i18n_hi.js → then guide.json). On slow 3G that chain alone was
about 11 s. Fonts and a 54 KB header photo shared the same thin pipe.

## Speed: before and after

Gzip + HTTP/2 (like the live site):

| | Slow 3G before | Slow 3G after | Fast 3G before | Fast 3G after |
|---|---|---|---|---|
| First paint | 5.2 s | 4.9 s | 1.4 s | 1.4 s |
| **Home shown** | **12.8 s** | **10.4 s** | **3.5 s** | **3.0 s** |
| Banner photo shown | 23.4 s | 12.7 s | 4.8 s | 4.3 s |
| Downloaded by the time Home shows | 567 KB | 314 KB | 569 KB | 469 KB |
| Downloaded until the page goes quiet | 1,544 KB | 600 KB | 992 KB | 928 KB |

A Hindi reader on slow 3G: Home 13.0 s → 10.8 s (one run).

`npm run serve` (no gzip, HTTP/1.1), for reference:

| | Slow 3G before | Slow 3G after | Fast 3G before | Fast 3G after |
|---|---|---|---|---|
| First paint | 10.6 s | 11.8 s | 2.6 s | 2.9 s |
| Home shown | 33.4 s | 29.4 s | 8.5 s | 7.5 s |
| Banner photo shown | 43.8 s | 31.6 s | 9.9 s | 9.0 s |
| Downloaded until quiet | 2,528 KB | 1,533 KB | 1,976 KB | 1,861 KB |

First paint is a little later here because the uncompressed 690 KB guide now downloads alongside the stylesheet. The
live site sends it gzipped (97 KB), where first paint got slightly faster.

### What changed

1. **The guide starts downloading first.** A one-line script at the top of `index.html` starts the `guide.json` fetch;
   `app.js` uses it (and fetches again if it failed).
2. **All modules load at once.** `index.html` has a `modulepreload` for every module `app.js` imports.
   `tests/js/shell.test.mjs` checks that list against the real import graph, so a new module can't be forgotten.
3. **Hindi strings load on demand.** `i18n.js` `loadLang('hi')` imports `i18n_hi.js` the first time someone picks
   Hindi (at start-up if Hindi was saved). English and Bengali readers skip 72 KB. `sw.js` still precaches it, so Hindi
   works offline.
4. **Fonts are no longer preloaded.** The preloads made fonts compete with the scripts. They still use
   `font-display: swap` and are in the offline cache, so the look is the same once they arrive.
5. **The header dhak button uses a 5 KB, 132 px crop** (`img/tiles/dhak-icon.jpg`) instead of the 720 px photo.
6. **On a slow connection the banner uses the 480 px photos** (`hero-N-sm.jpg`): when Chrome reports 2G/3G or
   Data Saver, or the app's low-data mode is on. Safari doesn't report connection speed, so it gets the full size as
   before. `scripts/hero_photo.py` now writes the small copies too.

### What we chose not to change

* **Trimming `guide.json`.** Every field is read by the app, `scripts/build_seo.py`, marketing or the tests, except
  `zones[].five_star` (about 200 bytes). The long `utm_` tails on Wikimedia photo URLs cost ~85 bytes each raw but
  almost nothing gzipped. Not worth touching a contract that marketing relies on.
* **Lazy-loading the tabs.** Home itself imports Routes and Explore (today's route card, search), and the remaining
  tabs are about 10 KB gzipped together. Splitting them would mean restructuring the views for a small gain, and
  modulepreload already removed the waterfall that made module count matter.
* **Splitting Bengali out of `i18n.js`.** Bengali readers are a core audience; this would only help English readers
  by ~15 KB.
* **The first-visit service worker download.** After Home shows, `sw.js` downloads the whole offline shell again
  (about 1 MB, `cache: 'reload'`). That is what makes the app work offline at the pandal, so it stays. A future pass
  could precache the 480 px hero instead of the full one.
* **The Bengali fonts on an English screen.** The header greeting (শুভ বিজয়া) is always in Bengali, so the two
  Bengali fonts load for everyone. Subsetting them to the greeting's letters would save ~150 KB but needs font tools
  we don't have in the repo.

## Accessibility: before and after

axe-core violations (counted per element):

| Screen | Light before | Light after | Dark before | Dark after |
|---|---|---|---|---|
| Home | 10 | 0 | 2 | 0 |
| Explore (pandal list) | 894 | 0 | 497 | 0 |
| Routes | 5 | 0 | 2 | 0 |
| My Pujo | 7 | 0 | 2 | 0 |
| Moments | 30 | 0 | 24 | 0 |
| Pandal page (sheet) | 32 | 0 | 20 | 0 |
| SOS page | 12 | 0 | 4 | 0 |

What they were: colour contrast (757), buttons whose spoken name didn't match their text (396), list rows using a
role a list item can't have (366), lists containing non-items (8), the hidden page sheet holding focusable buttons
(10), and the open page having no name (4).

### What changed

* **Contrast, by adjusting tokens, not the design.** Muted text `--ink-3` #84776C → #6F6359 (3.9:1 → 5.2:1 on the
  ivory). Brass text `--gold` #A27A2C → #80601E (now 4.8:1 even on the pale brass pill). Crowd pills mix their colour
  60/40 with the text colour, which darkens them in light mode and lightens them in dark mode (Quiet was 3.5:1 light,
  3.9:1 dark; now over 5:1). The SOS call button keeps a deep red in dark mode too (white on the dark theme's light
  red was 2.4:1). The WhatsApp button is a deeper green (white text 3.1:1 → 5:1).
* **Focus you can see.** The keyboard focus ring is sindoor (`--focus`, 2.5 px) instead of pale gold (2:1 on ivory),
  and ivory on the dark panels (banner, Pujo Radio).
* **List rows are real lists with real buttons.** Pandal, eatery and parking cards, "Hop next", nearby food, search
  results, the route timeline and the start picker no longer put `role="button"` on `<li>`. The row stays a list item
  (and keeps its heading) and the place name inside is a `<button>` (`rowBtn` in `state.js`), so a screen reader hears
  "Bagbazar Sarbojanin, button" inside a list. A tap anywhere on the row still opens it.
* **The page sheet is a proper dialog.** It is `inert` while closed, gets its name from its heading
  (`aria-labelledby`, or "Details" if it has none), makes everything behind it `inert` while open (so Tab and screen
  readers stay inside), and puts focus back where it was on close. Escape already closed it.
* **Names match what's on screen.** The SOS button is "Emergency numbers and SOS" (it says SOS); photo buttons are
  named by their photo instead of a different label. The SOS and tab-bar labels now follow the chosen language.
* **Tap targets.** The SOS pill and the sheet's × have invisible 44 px tap areas (same look); "I'm here" is 44 px tall.
* Already fine and left alone: `<html lang>` follows the language picker (en/bn/hi), toasts are `role="status"`
  `aria-live="polite"`, icon-only buttons have names, form fields have labels, reduced motion stops the slideshow.

New strings (English, Bengali, Hindi): `sheet.label` (Details / বিস্তারিত / विवरण), `tab.aria`
(Sections / বিভাগ / विभाग).

The e2e smoke test now also checks the keyboard path: focus a pandal name, Enter opens its page, the page has a name,
Tab stays inside, Escape returns focus to the pandal.

### Still open

* Filter chips (Explore, Moments) and the language picker are 32–36 px tall. They are secondary controls; making them
  44 px changes the header and filter rows, so it is left for a design decision.
* Only the seven screens above were scanned. The upload form, Routes wizard steps and food/parking pages use the same
  parts but weren't checked one by one.
* No test with a real screen reader (TalkBack, VoiceOver) was done.
