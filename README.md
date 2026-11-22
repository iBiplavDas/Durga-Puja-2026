# Pujo Parikrama 2026 🪔

A free, mobile-first guide to **Durga Puja 2026 pandal hopping in Kolkata and Howrah** (Shashthi 17 Oct → Dashami 21 Oct).

**Live:** https://pujoparikramaguide.in (mirror: https://shubhgptgrowth.github.io/Durga-Puja-2026/) · daily marketing kit: [/kit/](https://pujoparikramaguide.in/kit/)

It works in English, বাংলা and हिन्दी, installs as an app, and keeps working on weak networks.

> **Taking over?** Start with [docs/HANDOFF.md](docs/HANDOFF.md).

> **Status (November 2026):** the pujo is over. The app now opens with "See you at Pujo 2027" and a WhatsApp reminder sign-up; the guide, articles and routes stay up. Marketing continues on Instagram (Jagaddhatri, Chhath and other festivals). See [Before Pujo 2027](#before-pujo-2027) for what to fix first.

## What's in it

| | |
|---|---|
| Pandals | 169, in 5 regions (North, Central, South, East, Howrah) and 15 walkable areas |
| Eateries | 196, with signature dishes, cost, veg marks and opening hours |
| Parking | 16 car parks, plus car advice for every area |
| Transit | 56 metro and rail stations, OpenStreetMap bus routes and stops, common share-auto routes |
| Routes | 6 ready-made trails and a ready route for every pujo day, plus custom routes |
| Articles | 74 guide pages: rituals day by day, history, recipes, visiting tips, the VIP pass comparison, FAQs |

## The app

Four tabs:

| Tab | What it does |
|---|---|
| **Home** | Today's pandal route in one tap, and search across pandals, areas, eateries and dishes (English or Bengali names) |
| **Explore** | Pandals, Food and Parking lists. Each has a search box that looks across the whole city, plus filters: area, fame / nearest / quietest / most check-ins, 75+ years old, award winners, metro station; for food, veg, egg, sweets, street food, open now. Can't find a pujo? "Add a missing pujo" sends it to the team |
| **Routes** | A ready route for every pujo day, or your own in three steps: pick areas, then answer four questions with big buttons (which day, what time, how long, where from). The planner fills your time with the most famous pandals it can reach, rides only where a hop is over 1.8 km, and says how to travel each leg (walk, metro, bus, auto or cab). Routes open in Google Maps and can be shared as a link or on WhatsApp |
| **My Pujo** | Step counter (motion sensor, or GPS distance), check-ins, pandals visited, food logged, badges, history; Google sign-in keeps progress across phones. Photos & reels (**Moments**) open from here and from Home |

**Every pandal and eatery page** shows:
* live counts (visits, today, last hour) and an **I'm here / I ate here** button checked against your location (too far, and it offers a private "just for me" mark)
* the area address with a copy button, and **Directions**, which open Google Maps by the pandal's name
* crowd by hour and estimated footfall by puja day; this year's theme and awards where known
* photos credited to Wikimedia Commons (past idols and pandals; dishes for eateries)
* getting there: nearest metro, bus stops and routes, share autos, parking; nearby food, toilets, hospital and police
* that place's Moments

Also: an **SOS** sheet (national emergency numbers, nearest help, share where I am), Pujo Radio, restaurant offers and the iPhone Shortcut.

## How it's built

```
data/raw/*.csv ─► python -m pipeline ─► app/data/guide.json ─► app/ (static PWA)
                       │                                        │
                       └─► supabase/seed.sql ─► Supabase (check-ins, moments, sign-in) ◄┘
```

| Path | What |
|---|---|
| `data/raw/` | **Source of truth.** Regions, areas (`zones.csv`), pandals, food, parking and transit as CSV |
| `pipeline/` | Stdlib-only Python: ingest → validate → enrich → plan → emit. `discover` pulls open data, `discovered` merges new pandals and eateries, `pins` corrects pandal locations, `audit` / `audit_apply` check pins against OpenStreetMap |
| `data/seeds/`, `data/discovered/` | Well-known pujas to look up (each with its source), curated auto routes, and the raw open-data pulls |
| `app/` | Vanilla JS ES modules, no framework or build step. `views/` holds one module per tab; `sw.js` is the offline cache (bump `VERSION` when app files change) |
| `content/knowledge/` | The guide articles (Markdown), built into crawlable pages by `scripts/build_seo.py` |
| `supabase/` | Migrations (tables, row-level security, RPCs, storage), the generated seed, local stack config |
| `marketing/` | Daily content kit, carousels, reels, Instagram posting and engagement, reach reports (run by its own workflows) |
| `docs/` | **Product:** [roadmap](docs/product/ROADMAP.md), [scope](docs/product/SCOPE.md), [community backend](docs/product/COMMUNITY.md), [SEO](docs/product/SEO.md), [hosting](docs/product/HOSTING.md), [analytics](docs/product/ANALYTICS.md). **Marketing:** [plan](docs/marketing/PLAN.md), [tracker](docs/marketing/TRACKER.md) |
| `tests/` | Python pipeline tests, JS unit tests, SQL rule tests, and a Playwright mobile end-to-end test against a fake Supabase |

Every pandal, eatery and article is also a plain web page for search engines and AI assistants, with structured data, a sitemap and `llms.txt`. AdSense support exists but is off (`site.json`).

## Quick start

```bash
npm ci                         # dev only: Playwright
npm run build                  # python -m pipeline → app/data/*, supabase/seed.sql
npm test                       # Python + JS unit tests
tests/sql/run.sh               # community rules on a throwaway local Postgres
npm run test:e2e               # iPhone-size e2e against a fake Supabase (Chromium)
npm run serve                  # http://localhost:8123
```

Commit the rebuilt `app/data/` with any data change: CI fails when the bundle is stale. Community features stay off until `app/config.js` has a Supabase URL and anon key ([docs/product/COMMUNITY.md](docs/product/COMMUNITY.md)).

## Location accuracy

Pandal pins come from several sources, recorded in `geo_source`:

| `geo_source` | Count | Meaning |
|---|---|---|
| `osm`, `osm-discovered` | 64 | Matched to an OpenStreetMap feature. Usually close; some matches were a few hundred metres off |
| `osm-approx` | 72 | The centre of the neighbourhood, not the pandal. Marked "approximate" in the app |
| `curated` | 27 | Placed by hand, not checked on the ground |
| `commons-geotag` | 6 | Moved to where people photographed the pandal (Wikimedia Commons camera locations) |

Because of this, the app never sends people to a raw pin: **Directions open Google Maps by the pandal's name**, and pandal addresses show the **area and PIN only** until a pin is checked (`verified=true`).

To correct pins: run the **discover** workflow with `what=pins` (photo geotags and named parks), then `python -m pipeline.pins --dry-run`, review, and apply. It moves a pin only when the evidence agrees; titles must name the pandal exactly, a park named by several pandals is ignored, and two pandals are never moved onto one spot. With a `GOOGLE_MAPS_API_KEY` repository secret, `what=google` looks every pandal up on Google Maps (Places API) and `pipeline.pins` then prefers that listing and keeps its place id for Directions. Google's terms allow keeping its coordinates for 30 days, so re-run it each season.

Eateries and car parks keep their full street address.

## Adding data from open sources

The **discover** workflow (`.github/workflows/discover.yml`, run by hand with `what=`) runs `python -m pipeline.discover <what>` and commits the result to `data/discovered/`:

| `what` | Pulls |
|---|---|
| `pandals` | Durga Pujas tagged in OpenStreetMap, plus a lookup for each puja in `data/seeds/pandal_seeds.csv` |
| `food` (or `food:<area>+<pandal_id>`) | Restaurants, sweet shops and street food near pandals |
| `transit` | Bus and share-taxi routes, stops, taxi and auto stands |
| `photos` | Wikimedia Commons photos per pandal and per signature dish |
| `help` | Public toilets, hospitals and police stations |
| `addresses` | The address of every place (Nominatim reverse lookup; slow, one a second) |
| `pins`, `google` | Location evidence for pandal pins (above) |

Then `python -m pipeline.discovered pandals|food [--dry-run]` merges confident new places into `data/raw/`; review the ADD and skip lines before applying. New pandals stay out of the published walking routes (`route=skip`). After places change, re-run **supabase-setup** so the backend knows them, then the **deploy**.

Limits: OSM bus coverage in Kolkata is thin; share-auto routes are mostly the curated list in `data/seeds/auto_routes.csv`; dish photos show the dish, not that shop; `data/raw/photo_blocklist.csv` removes wrong photo matches.

## CI and deploys

* **pipeline:** Python tests, data validation, a rebuild with a check that the committed bundle and seed are fresh, JS unit tests and the mobile e2e test.
* **deploy:** publishes `app/` on every push to the default branch and every morning (05:45 IST), with the content kit at `/kit/`, then verifies the live site.
* **supabase-setup:** applies migrations and the seed. **discover:** open data (above). **geo-audit**, **indexnow**, **analytics-report** and the marketing workflows (`marketing-*`, `reels-factory`, `engage`, `giveaway`, `ig-dm-*`) run on their own schedules.

## Before Pujo 2027

* Confirm pandal locations: add `GOOGLE_MAPS_API_KEY` and run `what=google`, or check the big pandals by hand, then mark them `verified`.
* Review "Add a missing pujo" suggestions in Supabase (`analytics.pujo_suggestions`) and add the real ones.
* Update dates, themes, awards and VIP passes for 2027; re-run `discover` for photos, food and addresses.
* Check the route timings (about 25–30 minutes inside a big pandal at peak) against real queues.

## Data disclaimer

Themes, timings, crowds and traffic rules change every year, and some locations are approximate. The app says so, and asks people to check locally.
