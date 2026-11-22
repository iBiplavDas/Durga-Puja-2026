# Product roadmap: the app at pujoparikramaguide.in (refreshed 22 Nov 2026)

This track covers everything the app does: data, features, backend, hosting and quality.
Marketing lives in [../marketing/](../marketing/). The seam between the two tracks is at the end.
For the full picture (rules, architecture, history, traps), read [../HANDOFF.md](../HANDOFF.md) first.
The business side is in [BUSINESS_ROADMAP.md](BUSINESS_ROADMAP.md) (year 1) and [PLAN_100CR.md](PLAN_100CR.md) (to March 2029).

**Owns:** `app/`, `pipeline/`, `data/`, `supabase/`, `tests/`, and the `pipeline`, `deploy`, `discover`, `geo-audit` and
`supabase-setup` workflows.

## Key dates

| Date | Milestone | What must be true |
|---|---|---|
| ✅ 10–21 Oct 2026 | Pujo 2026 (Mahalaya → Dashami) | Done. The app now says "See you at Pujo 2027" with a WhatsApp reminder sign-up |
| Dec 2026 – Mar 2027 | Off-season build | Backlog below; committee portal pilot; footfall reports and media kit for sales (business track) |
| **1 Jun 2027** | Media kit to brands | Real 2026 numbers; sponsor slots work and can be switched off from config |
| **Jul 2027** | Pujo 2027 season starts | 2027 dates live; pins verified for the top pandals; `route=skip` cleared where checked; search pages refreshed |
| Mahalaya 2027 | Marketing launch push | Capacity upgrades decided (paid Supabase plan is an owner/billing decision) |
| Panchami 2027 | Code freeze | Only data fixes and hotfixes after this |

## Where the app is today (22 Nov 2026)

* **Coverage:**
  * 169 pandals: 125 from before 17 Oct, plus 44 added from open-source seeds on 17 Oct. Those 44 carry `route=skip`, so they appear in lists but not in zone routes.
  * 196 eateries, including Howrah.
  * 16 car parks, 56 stations, 15 areas, 5 regions.
  * 6 trails, plus a route for each pujo day.
  * 74 guide articles that double as SEO pages.
* **Pins:** none are ground-verified. By source:

  | Source | Pins | Notes |
  |---|---|---|
  | `osm` and `osm-discovered` | 64 | Some are a few hundred metres off |
  | `osm-approx` | 72 | Neighbourhood centre |
  | `curated` | 27 | Placed by hand, unchecked |
  | `commons-geotag` | 6 | Moved to where Commons photos were taken |

  **Mitigations:**
  * Directions open Google Maps by pandal name.
  * Addresses show area and PIN only until a pandal is `verified=true`.
  * Approximate pins get a wider check-in radius (600 m; OSM pins 250 m; others 350 m).
* **Features:**
  * Four tabs (Home, Explore list and search, Plan routes, Me).
  * Moments, GPS-verified check-ins, "I ate here".
  * Crowd by hour, transit legs, food and parking nearby.
  * SOS sheet, addresses with a copy button, "Add a missing pujo".
  * Step counter and badges, Pujo Radio, Google sign-in with progress sync, delete-my-data.
  * Restaurant offers.
  * English, Bengali and Hindi; works offline.
* **Hosting:**
  * https://pujoparikramaguide.in on GitHub Pages.
  * After the repo moved to `iBiplavDas/Durga-Puja-2026`, `ibiplavdas.github.io/Durga-Puja-2026/` redirects to the domain (checked 22 Nov).
  * **The old `shubhgptgrowth.github.io` mirror returns 404**, so QR codes printed with it are broken (see [HOSTING.md](HOSTING.md)).
* **Quality gates:**
  * Python tests (`python -m unittest discover -s tests`), JS tests (`node --test tests/js/*.test.mjs`) and SQL tests (`tests/sql/run.sh`).
  * A Playwright smoke test against a fake Supabase.
  * A live-site check after every deploy.

## Shipped since the 3 Oct roadmap

| Item (old #) | Status |
|---|---|
| Custom domain (P0-2) | ✅ pujoparikramaguide.in |
| Map tiles (P0-3) | ✅ built, then the in-app map was removed (Explore is a list). Leaflet and Protomaps vendor files were deleted 22 Nov |
| 2026 themes plumbing (P1-1) | ✅ `data/raw/themes_2026.csv`; each row needs an https source |
| Howrah coverage (P1-5) | ✅ partly: Howrah eateries and pandals added; OSM coverage there is thin |
| Hindi UI (P2-5) | ✅ |
| Traffic notices (P2-3) | ✅ `traffic-fetch` Edge Function + `traffic_notices` |
| The 5 missing well-known pujas (P0-5) | 🟡 the 17 Oct seed run added 44 pandals, but Sikdarbagan, Pathuriaghata, Darjipara, Kestopur Prafulla Kanan, Salkia Sarbojanin and others are among the 35 seeds still unplaced |
| **Error and quota monitoring (P0-6)** | ✅ 22 Nov: client error beacon → `log_client_error` → `analytics.client_errors_daily`, plus an errors section in the daily report |
| **Crowd report button (P1-4)** | ✅ 22 Nov: "How's the queue here? Short / Medium / Long" on pandal sheets, accepted only near the pandal; an aggregate is shown only with ≥3 recent reports |
| **Moments moderation view (P1-7)** | ✅ 22 Nov: `analytics.moments_queue` and `moderate_moment(id, action)` (SQL editor only) |
| **Performance pass (P1-8)** | ✅ 22 Nov: see [PERF_A11Y.md](PERF_A11Y.md) |
| **Accessibility pass (P1-9)** | ✅ 22 Nov: see [PERF_A11Y.md](PERF_A11Y.md) |

## Backlog

Priority: **P0** = needed before the Pujo 2027 season starts (July 2027). **P1** = before Mahalaya 2027.
**P2** = nice to have. Status: ⬜ todo · 🟡 in progress · ✅ done · ⏸ waiting on the owner.

### Waiting on the owner

| # | Item | Status |
|---|---|---|
| O-1 | **`GOOGLE_MAPS_API_KEY`** (Places API (New), billing on). This switches on `discover what=google`, then `pipeline.pins` matches all 169 pandals to their Google listing and stores place IDs. ~169 requests a run; expected within the free allowance, not guaranteed. Alternative: Google Maps share links for the top 20–30 pandals | ⏸ cost decision |
| O-2 | **Old QR codes:** the `shubhgptgrowth.github.io/Durga-Puja-2026/` mirror is 404. Only the `shubhgptgrowth` account can bring back a redirect page. Also point the domain's DNS CNAMEs at `ibiplavdas.github.io` if they still name the old account ([HOSTING.md](HOSTING.md)) | ⏸ |
| O-3 | Business decisions in [BUSINESS_ROADMAP.md](BUSINESS_ROADMAP.md) Part 5 and [PLAN_100CR.md](PLAN_100CR.md) §7 | ⏸ |
| O-4 | Paid Supabase plan for the 2027 season | ⏸ billing |

### P0: data accuracy before Pujo 2027

| # | Item | Why | Status |
|---|---|---|---|
| D-1 | **Verify pins** (ground check, or Google after O-1). Mark `verified=true`, clear `route=skip` for checked new pandals, and run `supabase-setup` | A wrong pin breaks check-in and directions. Data accuracy is the owner's top concern | ⬜ |
| D-2 | **Review `pujo_suggestions`** (`analytics.pujo_suggestions`; mark with `review_pujo_suggestion(id, status)`) and add the real ones with a source | Visitors told us what's missing | ⬜ |
| D-3 | **The 35 unplaced seeds:** 24 had no confident match (e.g. Sikdarbagan, Pathuriaghata, Darjipara, Kestopur Prafulla Kanan, Salkia Sarbojanin, Belur, Beadon Street), and 11 were outside every area (Thanthania, Laha Bari, Baranagar, Belgharia, Sodepur, Tala Barowari…). They need addresses or new areas | People search for them | ⬜ needs local help |
| D-4 | **2027 data:** dates, themes (each with an https source), awards, VIP passes (update `/durga-puja/pujo-pass/`), fresh photos, food and addresses | It's the first thing people ask | ⬜ from Jul 2027 |
| D-5 | **Validate route timings** (25–30 min inside a big pandal at peak) against real queues, using this season's crowd reports | Routes promise counts that marketing repeats | ⬜ |

### P1: product

| # | Item | Why | Status |
|---|---|---|---|
| P1-1 | **Bengali names for the 31 `osm-discovered` pandals** (from OSM `name:bn` or a sourced spelling; never guessed) | The Bengali UI shows English names for them | ⬜ |
| P1-2 | **"Add to home screen" prompt** after a first check-in or a saved plan | Repeat use during the 5 days | ⬜ |
| P1-3 | **Footfall report generator (M5)**: one page per pandal from verified check-ins plus the crowd model, aggregates only | Sells the committee tier and sponsors ([BUSINESS_ROADMAP.md](BUSINESS_ROADMAP.md)) | ⬜ |
| P1-4 | **Media kit page (M9)** from the reach report | Brand sales by 1 Jun 2027 | ⬜ |
| P1-5 | **Committee portal pilot (M6)**: claim your pandal, theme, timings, photos, live count | Data quality and B2B revenue | ⬜ |
| P1-6 | **Multi-festival engine (M7)**: generalise pandal → venue and puja days → event days, with one data folder per event | Kali Puja, Chandannagar, Book Fair, CR Park, Mumbai Ganesh | ⬜ |
| P1-7 | Crowd reports: show the live signal on the Plan tab and in route timings once there's enough data | Turns the crowd curve from a model into a measurement | ⬜ |

### P2: later

| # | Item |
|---|---|
| P2-1 | Curated bus routes (OSM has only 21 for Kolkata) and auto fares, with sources |
| P2-2 | Group plans: turn a plan into a shareable "our pujo route" where friends vote |
| P2-3 | A year-in-review page per device, built from local history |
| P2-4 | An offline area pack, if a map comes back |
| P2-5 | Tours and walks booking (M8) |

## How a change ships

1. Work on a feature branch and open a PR into `claude/kolkata-durga-puja-guide-4t5xad`, the default branch. **Every push to it deploys.**
2. **Data:**
   * Edit `data/raw/*.csv`, or run `discover` → `python -m pipeline.discovered pandals`.
   * Then run `python -m pipeline` and commit the regenerated `app/data/*` and `supabase/seed.sql`. CI fails with "guide.json is stale" otherwise.
3. **Code:** edit `app/`, then run `python3 -m unittest discover -s tests`, `node --test tests/js/*.test.mjs`, `tests/sql/run.sh` and `node tests/e2e/smoke.mjs <outdir>`. `npm test` skips the JS tests if Python fails, so run them separately.
4. **App changes:** bump `VERSION` in `app/sw.js`, and add new JS files to its `SHELL` list.
5. Push or merge. The `pipeline` workflow runs everything again, and `deploy` publishes and checks the live site.
6. **If places, coordinates or migrations changed, run `supabase-setup`.** Deploy's live check fails on place counts until it has run, and new RPCs don't exist until it has.
7. **Open-data work goes through workflows.** Run `discover`, `geo-audit` or `pins --dry-run` and review the output before applying it. Name-word matches catch the wrong puja.

## What marketing relies on (the seam)

Don't break these without telling the marketing track:

| Contract | Where | Used by |
|---|---|---|
| Link codes: `?src=<a-z0-9_ up to 40>` | `app/growth.js` `captureSource()`, `public._clean_src()` | Every post, poster and partner link |
| Direct links: `#p=<place id>` | `app/app.js` | QR posters, WhatsApp shares, comment replies. **Renaming a place id breaks printed posters** |
| Place ids and names | `app/data/guide.json` | `marketing/kit.py` builds every card from it |
| Route counts per zone and day | `app/views/plan.js` `DAYPLAN`, the zone routes | Voiceovers ("17 pujos in one night") and carousels capped at 10 slides. Changing pandals in zones changes them |
| Reach counting | `track_open()`, `growth_report()` in `supabase/migrations/*_growth.sql` | The `marketing-report` workflow |
| Share UI | WhatsApp, Story card and Link buttons on sheets; My Pujo card on Me. Place shares link to `guide/pandals/<id>/?src=…` | The viral loop |
| Public address | `site.json` (`url`, `pages_url`; change with `python scripts/site.py set …`) | All links, the kit, QR posters and link previews |
