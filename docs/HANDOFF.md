# Handoff: Pujo Parikrama (as of 22 Nov 2026)

Everything someone taking over needs: what the product is, where it runs, how it's built, what was done, what was
decided, the rules the owner set, the traps we hit, and what's planned next. Read this first, then
[README.md](../README.md) for the code tour.

---

## 1. The product in one paragraph

**Pujo Parikrama** is a free, mobile-first web app (an installable PWA) for **Durga Puja pandal hopping in Kolkata and
Howrah**, built for the 2026 pujo (Mahalaya 10 Oct; Shashthi 17 Oct to Dashami 21 Oct). It lists 169 pandals, 196
eateries and 16 car parks; plans walking routes by day, time and area; shows crowds by hour, transit, food and help
nearby; and has check-ins, photo/video "Moments", a step counter and Google sign-in. English, Bengali and Hindi.
There are also 74 guide articles that double as SEO pages. A marketing engine (Instagram carousels, reels, stories,
auto-posting, engagement) runs alongside. The pujo is over; the app now says "See you at Pujo 2027" with a WhatsApp
reminder sign-up, and the Instagram account carries on with other festivals.

## 2. Where everything lives

| What | Where |
|---|---|
| Live app | https://pujoparikramaguide.in (custom domain on GitHub Pages) |
| Old mirror | `shubhgptgrowth.github.io/Durga-Puja-2026` — **may be dead**: see the repo move below |
| Daily marketing kit | `/kit/` on the live site; team dashboard at `/kit/dashboard/`, reels catalogue at `/kit/reels/` |
| Repository | **Moved to `github.com/iBiplavDas/Durga-Puja-2026`** (was `shubhgptgrowth/Durga-Puja-2026`; GitHub redirects pushes). Update `site.json` `pages_url`, the README mirror link and any `shubhgptgrowth` links once the new Pages address is confirmed |
| Working / default branch | `claude/kolkata-durga-puja-guide-4t5xad`. **Every push to it deploys.** Other Claude sessions also work through PRs (`claude/clever-cannon-*` for marketing, `claude/nifty-dijkstra-*`, `claude/cool-bell-*`) that merge into it |
| Backend | Supabase (project config in `app/config.js`; migrations in `supabase/migrations/`) |
| Docs | `docs/product/` (roadmap, scope, community backend, SEO, hosting, analytics, AdSense, offers, Google sign-in, iPhone Shortcut, business roadmap) and `docs/marketing/` (plan, strategy, tracker, content, creators, press, social calendar, featured offers) |

GitHub secrets the workflows use (names only): `SUPABASE_ACCESS_TOKEN`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`,
`IG_ACCESS_TOKEN`, `IG_PAGE_ID`, `IG_USER_ID`, `PAGES_ADMIN_TOKEN`, `CONTACTS_PASSPHRASE`, `PEXELS_API_KEY`,
`PIXABAY_API_KEY`, and `GOOGLE_MAPS_API_KEY` (**referenced but not yet added**, see §8).

## 3. Rules the owner set (keep following these)

* **Develop and push only on the working branch**; open PRs only when asked.
* **Never fabricate data.** No invented pandals, eateries, prices, rates or themes. Every 2026 theme row needs an https
  source. Unknown is better than made up.
* **Don't copy competitors' data or text** (thepujo.com was reviewed for inspiration only).
* **No phone numbers or secrets in git, logs or plain artifacts.** Exception the owner allowed: the public Porikroma
  helpline in the VIP-pass article. Forms collect no phone/email unless the feature is explicitly about that (the
  2027 WhatsApp reminder, which stores contacts encrypted).
* **Don't spend money without asking** (Supabase Pro, Google APIs, paid tools).
* **Don't claim human review that didn't happen.**
* **Leave `marketing/` to the marketing sessions** unless asked.
* Commits carry the trailers `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` and a `Claude-Session:` line;
  no model names in code or commit text.
* Data accuracy is the top product concern: the owner's words were "people won't use the app if there's data accuracy
  issues". Prefer showing less (area instead of street, Google by name instead of our pin) over showing something wrong.
* Core modules (pandals, routes, food) must never be overpowered by promos (VIP passes were demoted to a quiet row).
* The app must stay usable for non-tech-savvy people: big buttons, plain words, few choices up front.

## 4. How it's built

```
data/raw/*.csv ─► python -m pipeline ─► app/data/guide.json ─► app/ (static PWA, vanilla JS)
                       │                                        │
                       └─► supabase/seed.sql ─► Supabase ◄──────┘  (check-ins, moments, sign-in, analytics, offers)
```

* **`data/raw/`** is the source of truth (regions, zones, pandals, food, parking, transit, themes, awards…).
* **`pipeline/`** (stdlib Python): `ingest → validate → enrich → plan → emit`, plus
  `discover` (open-data pulls, run in CI), `discovered` (merge new pandals/eateries), `pins` (move pandal pins on
  evidence), `audit`/`audit_apply` (OSM checks).
* **`app/`**: ES modules, no framework or build. `views/` = one module per tab (home, explore, plan, me, moments).
  `sheets.js` = place pages, SOS, addresses. `sw.js` = offline cache (**bump `VERSION` on every app change**; new JS
  files must be added to its SHELL list).
* **`content/knowledge/`** → `scripts/build_seo.py` → crawlable pages, JSON-LD, sitemap, `llms.txt`.
* **`supabase/migrations/`**: community, growth, traffic, ratings/profiles, contacts, analytics, site counts,
  progress sync, offers/menus, delete-my-data, featured offers, dashboard, reels stats, IG DMs, place popularity,
  pujo suggestions.
* **Workflows** (`.github/workflows/`): `pipeline` (tests + freshness), `deploy` (push + 05:45 IST daily + verify),
  `supabase-setup`, `discover`, `geo-audit`, `indexnow`, `analytics-report`, `traffic*`, `offers`, `contacts-export`,
  and the marketing set (`marketing-*`, `reels-factory`, `engage`, `story-check`, `footage-scan`, `music`, `audio`,
  `narrate`, `hero-photo`, `article-photos`, `giveaway`, `ig-dm-*`, `shortcut`, `preview`).

Commands: `npm run build`, `npm test` (Python then JS — note the JS part doesn't run if Python fails; run
`node --test tests/js/*.test.mjs` separately), `node tests/e2e/smoke.mjs <outdir>` (Playwright, fake Supabase),
`python -m unittest tests.test_build_seo`, `npm run serve`.

## 5. Current data state

| | |
|---|---|
| Pandals | 169 (125 before 17 Oct + 44 added from open-source seeds on 17 Oct) |
| Eateries | 196 (incl. Howrah) · Parking 16 · Stations 56 · Areas 15 · Regions 5 |
| Ready routes | 6 trails + a route per pujo day (in `app/views/plan.js` `DAYPLAN`) |
| Articles | 74 |

**Pin sources** (`geo_source`): `osm` + `osm-discovered` 64 (OSM matches, some a few hundred m off), `osm-approx` 72
(neighbourhood centre, flagged "approximate"), `curated` 27 (hand-placed, unchecked), `commons-geotag` 6 (moved to
photo locations on 18 Oct). **None are ground-verified.**

Mitigations live in the app: Directions open Google Maps **by pandal name** (`pandalDirUrl` in `sheets.js`, and
`destination_place_id` once `gplace` exists); pandal addresses show **area + PIN only** until `verified=true`;
approximate pins get a wider check-in radius (600 m; OSM 250 m; others 350 m).

The 44 pandals added on 17 Oct carry `route=skip`: they're on the map and lists but **not in the zone walking routes or
itineraries**, because published marketing (voiceovers saying "17 pujos in one night", carousels capped at 10 slides)
depends on the route counts. Clear `route` per pandal once its pin is checked.

## 6. What was built (chronological)

**Before the festival (late Sep – 16 Oct)**
* Core app: pandals, food, parking, transit, crowd-by-hour model, on-device route planner, curated trails, day-by-day
  "all of Kolkata" plan, metro/bus/auto/cab legs, Google Maps export.
* Community backend: check-ins verified by GPS (private "just for me" fallback), Moments feed with uploads, likes,
  reports; live counts; reach tracking; analytics; ratings; Google sign-in with progress sync; delete-my-data.
* Look and feel: classy "lal-paar" design system, Baloo/serif fonts, festive header with rotating protima banner and
  pujo lingo, live pill and stats ticker, photo tiles, Pandals/Food/Parking switcher.
* Features: Pujo Radio (YouTube embeds, dhak on first tap), estimated footfall, step counter (motion/GPS, Health app
  link), badges, restaurant offers and menu photos (paid "Sponsored" featured offers), iPhone Shortcut, Hindi UI.
* Maps: self-hosted Protomaps tiles were built; the in-app map was later removed (Explore is a list; directions go to
  Google Maps).
* Content/SEO: ~56 knowledge articles in two rounds (rituals by day, history, recipes, festivals, visiting, FAQ),
  Wikimedia Commons photos, reading-first page design, structured data (Article/HowTo/Recipe/DefinedTermSet), image
  sitemap, IndexNow, 404, About/Contact/Terms, AdSense readiness (off), 2026 themes plumbing.
* Data: OSM geo-audit (Oct) corrected 58 pins; discovered pandals, transit, photos, help places.
* Marketing engine (separate sessions): daily content kit, carousels, reels factory, auto-publishing to Instagram,
  reach report, engagement/DM tooling, creators list, giveaway.

**17–19 Oct (this working thread)**
* Howrah eateries added (targeted OSM pulls; Howrah OSM coverage is thin — reported honestly).
* **VIP pass article** `/durga-puja/pujo-pass/`: Porikroma Map Invitee Card vs FFD Pujor Passport, with the public
  helpline; passes demoted to a quiet row on Home.
* Removed the Home Ashtami/Sandhi card.
* **Addresses** on every pandal/eatery page (Nominatim reverse geocode in CI), with a **copy button**.
* **Moments uploads fixed** for phones (HEIC via heic2any, untyped files, huge images).
* **SOS sheet** (112/100/108/101/1091/1098, nearest hospital/police/toilet, share where I am).
* **+44 pandals** from news, award lists and Wikipedia seeds (each seed has a source column), Bengali names for all.
* **"Add a missing pujo"** form → `suggest_pujo` RPC → `public.pujo_suggestions` (no phone/email; 10/day/device);
  review in `analytics.pujo_suggestions`, mark with `review_pujo_suggestion(id, status)`.
* **Explore search** across pandals, food, parking (whole city, every word must match).
* **Location accuracy work**: Directions by name; area-only addresses; `discover pins` (Commons geotags + named parks)
  and `pipeline.pins` with strict evidence rules (exact title words, no shared parks, no two pandals on one spot);
  6 pins moved; `discover google` built but off (no key).
* **Bottom tab bar** fixed (4 tabs on a 5-column grid → even).
* **Routes simplified**: step 2 is four questions with big buttons (day, time, how long, where from); travel mode
  moved to the result; plain wording.
* **Routes pack more pandals**: greedy pick by fame-per-minute from the start, one walk across areas (ride only for
  hops > 1.8 km), trim/top-up to the time budget, default 3★+. E.g. South 2 h: 1 → 4; North all night: 14 → 18.
* README rewritten (15 Nov).

**After the festival (other sessions)**: Dashami goodbye content, "See you at Pujo 2027" + WhatsApp reminder
sign-up, Bijoya/Chhath/Hanuman/Jagaddhatri/Dev Deepawali reels, an audit of the first 50 Instagram posts ("timing
beats format; photos don't travel"; story reels at 0.3–0.6× median views), comment-to-DM turned off, social calendar
extended to 27 Dec.

## 7. Operational lessons (traps we hit)

* **Commit the rebuilt bundle.** CI fails with "guide.json is stale" if `app/data/` doesn't match `python -m pipeline`.
  Discover runs commit data but don't always rebuild — pull and rebuild after them.
* **After place counts or coordinates change, run `supabase-setup`**, or deploy's verify step fails on place counts and
  check-ins use old pins.
* **Deploys**: occasionally hang at Playwright install (cancel after ~15 min, re-run); verify sometimes fails on a TLS
  handshake glitch (re-run failed jobs once). Pending deploys get superseded.
* **The Claude sandbox can't reach the live site, Overpass or Nominatim** — do open-data work through the `discover`
  workflow; GitHub access is via the GitHub MCP tools.
* **Tests that depend on today's date** break during the festival (fixed for the day chips; watch for others).
* **Route counts are referenced by marketing** (voiceovers, carousels). Changing pandals in zones changes them.
* **Evidence matching is fragile**: name-word matches catch the wrong puja (Tala Prattoy vs Tala Barowari;
  "Dum Dum Park" is a neighbourhood, not a park). Always review `--dry-run` output before applying.
* **Google Places terms**: place IDs can be stored indefinitely, coordinates only 30 days — re-run `what=google` each
  season; don't publish Google addresses.

## 8. Open items and future plans

### Waiting on the owner
1. **`GOOGLE_MAPS_API_KEY`** (Places API (New), billing on): enables `discover what=google` → `pipeline.pins` to pin all
   169 pandals to their Google listing and store place IDs. ~169 requests per run; expected within Google's free
   allowance but not guaranteed. Alternative: Google Maps share links for the 20–30 most important pandals.
2. **Confirm the new GitHub Pages address** after the repo move and update `site.json`, README, and old links.
3. Business decisions in `docs/product/BUSINESS_ROADMAP.md` §5 (business vs passion project, selling now, AdSense,
   second festival, 2027 scope).

### Data (before Pujo 2027)
* Ground-check / Google-verify pins; mark `verified=true`; clear `route=skip` for checked new pandals; consider
  widening check-in for still-unconfirmed pins.
* Review `pujo_suggestions`; add real pujas.
* Seeds the 17 Oct run couldn't place: 24 with no confident match (e.g. Sikdarbagan, Pathuriaghata, Darjipara,
  Kestopur Prafulla Kanan, Salkia Sarbojanin, Belur, Beadon Street) and 11 "outside every area" (Thanthania, Laha
  Bari, Baranagar, Belgharia, Sodepur, Tala Barowari…) — need addresses or new areas.
* 2027 dates, themes (with sources), awards, VIP passes (update the pass article); fresh photos, food and addresses.
* Validate route timings (25–30 min inside a big pandal at peak) against real queues; consider a crowd-report button.

### Product backlog carried from `docs/product/ROADMAP.md` (some items are stale — the roadmap itself needs a refresh)
* Shipped since it was written: custom domain, Hindi UI, map tiles (then the map was removed), 2026 themes plumbing.
* Still open: error/quota monitoring, add-to-home-screen prompt, crowd report button, Moments moderation view,
  performance pass (guide.json size), accessibility pass, curated bus routes and auto fares, group plans, a
  year-in-review page, Bengali names for the 31 `osm-discovered` pandals.
* Supabase Pro during the festival was an owner/billing decision.

### Growth and business (from `BUSINESS_ROADMAP.md`, owner approval pending)
* Same engine for more festivals (Kali Puja, Chandannagar Jagaddhatri, Bengal's calendar), Durga Puja beyond Kolkata
  (probashi), other Indian crowd festivals (2027+), and an owned audience (WhatsApp list started) so each season starts
  warm.
* Revenue ranked by speed: featured offers (built), title sponsor, AdSense on guide pages only (never in the app), …
  with the rule that paid placements never change crowd advice.

### Housekeeping
* `docs/product/ROADMAP.md` still describes 3 Oct; refresh it from this handoff.
* README mirror link and `site.json` `pages_url` (repo move).
* `app/vendor/leaflet` and `protomaps-leaflet` are no longer used by the app (only listed in `sw.js`); remove or keep
  for a future map.

## 9. Quick start for the next owner

```bash
git clone https://github.com/iBiplavDas/Durga-Puja-2026 && cd Durga-Puja-2026
git checkout claude/kolkata-durga-puja-guide-4t5xad
npm ci && npm run build && npm test && node --test tests/js/*.test.mjs
npm run serve            # http://localhost:8123
```

Change data in `data/raw/`, rebuild, run tests, bump `sw.js` `VERSION` for app changes, commit `app/data/` with it,
push, then watch `pipeline` and `deploy`. Run `supabase-setup` when places change.
