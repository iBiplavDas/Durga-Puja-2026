# The ₹100 crore plan: from a pujo guide to India's festival platform by March 2029 (draft, 22 Nov 2026)

> For the owner. It builds on [BUSINESS_ROADMAP.md](BUSINESS_ROADMAP.md), which covers year 1, and on the facts in
> [../HANDOFF.md](../HANDOFF.md). Every number is marked as **sourced** (with a link), **ours** (from this repo), or
> an **assumption** (a target we have to prove). Nothing here is a forecast we can already back with data.

## 0. What "₹100 crore" means here, and the honest odds

There are two readings, and they need very different plans:

| Reading | What it takes by March 2029 | Odds from where we stand |
|---|---|---|
| **A. ₹100 crore revenue in FY 2028-29** (Apr 2028 – Mar 2029) | About 20–30× growth in each of the next two years, a national festival business with 80–150 people, and outside capital | **Low.** It's possible only if Pujo 2027 is a breakout and we raise money on it. Plan for it, but gate every step |
| **B. A ₹100 crore valuation** (a priced funding round or an acquisition offer) | About ₹8–15 crore of revenue growing fast, or a strategic buyer (a food, ticketing, media or tourism player) who wants the audience, the data and the engine | **Realistic but hard.** This is the base case |

**The plan below aims at A and treats B as the floor.** The gates in §5 say when to switch the goal from A to B.
Being honest about this protects the owner's money and time.

### Where we start (ours, 22 Nov 2026)

* **The product:** a free web app covering 169 pandals, 196 eateries and 74 guide articles, in Bengali, English and Hindi. It works with no install.
* **The engine:** routes and crowds by hour, plus GPS-verified check-ins. That gives us footfall data that almost nobody else has.
* **Instagram:** a median reel gets about **270 views**. The best post, a route timed to the night people went out, got **20,353 views, 238 shares and 256 saves** ([audit](../../marketing/briefs/audit-2026-11-15.md)). Photos and late posts don't travel.
* **Revenue:** **₹0** so far. Featured offers were put on hold on 7 Oct at about 170 devices ([FEATURED_OFFERS.md](../marketing/FEATURED_OFFERS.md)).
* **Season totals:** total devices and check-ins for Pujo 2026 aren't written down in the repo. **First task:** copy them from the `marketing-report` / `analytics-report` output into §6. Every gate below is measured against them.
* **Competitors:** Kolkata Police's Puja Bandhu, WB Tourism, Utsav, Swiggy ShresthoPujo and one-season brand apps ([BUSINESS_ROADMAP.md](BUSINESS_ROADMAP.md) §4b).

### Why the prize is real (sourced)

* **The Durga Puja creative economy in West Bengal was about ₹32,377 crore** in 2019, about 2.6 % of state GDP ([British Council study](https://www.britishcouncil.in/sites/default/files/mapping_the_creative_economy_around_durga_puja_sept_2021.pdf)). Industry estimates for 2025 range from **₹46,000–50,000 crore** ([Deccan Herald](https://www.deccanherald.com/india/west-bengal/west-bengals-2025-durga-puja-economy-rebounds-by-10-15-to-rs-4600050000-crore-3747970)) up to about ₹65,000 crore ([Open](https://openthemagazine.com/india/faith-festivity-65000-crore-how-durga-puja-puts-bengal-to-work)).
* **Puja outdoor advertising in West Bengal** is estimated at **₹800–1,000 crore over 10 days**. Brands put **20–30 %** of their festive budgets into Durga Puja ([Storyboard18](https://www.storyboard18.com/advertising/durga-puja-ad-spends-surge-15-led-by-fmcg-auto-and-e-commerce-81275.htm), [exchange4media](https://www.exchange4media.com/festive-season-news/durga-pujas-hidden-ooh-economy-is-adex-missing-a-chunk-158786.html)). **Almost none of this spend can be measured today.** That gap is our opening.
* **India's festive ad spend** was about **₹45,000–60,000 crore in 2025** ([The Current](https://www.thecurrent.com/marketing-strategy-dussehra-diwali-india-ad-budgets-ctv)).

₹100 crore of revenue is about 0.2 % of festive ad spend. The money exists. What's missing is **distribution** (people who use us) and **proof** (data brands trust).

## 1. The business we'd have to become

**One line:** *the crowd-and-route layer for India's festivals.* People use it free. Brands, organisers and governments
pay for reach, measurement and operations.

There are four engines. Each builds on the one before it:

1. **Audience.** A free festival guide for each festival and city, Bengali-first and then multilingual, with no install, shared on WhatsApp. This is the funnel, not the business.
2. **Data.** Verified footfall by place and hour, crowd reports (built 22 Nov 2026), check-ins, and how people move. It's sold **only in aggregate**, never as personal data. That's the brand promise and the law (the Digital Personal Data Protection Act, 2023).
3. **Software.** A portal for puja committees and organisers (claim your pandal, themes, timings, footfall, sponsor reports), plus a white-label crowd-and-route guide for governments, tourism boards, police and event organisers.
4. **Transactions.** Passes, guided walks, darshan and queue slots where organisers allow them, food pre-orders near pandals, and hotel and travel affiliates.

**These rules carry over unchanged:**
* Paid placements never change crowd advice, routes or rankings.
* Every paid placement is labelled Sponsored.
* No personal data is ever sold.
* Ads appear on guide pages only, never in the core app flows.

## 2. Revenue model for FY 2028-29: what ₹100 crore would be made of (assumptions)

| Line | Who pays | Unit assumption | FY 28-29 target |
|---|---|---|---|
| **Brand partnerships across the festival calendar** (title sponsors, sponsored trails, story frames, creator content) | FMCG, sweets, ethnic wear, telecom, paints, two-wheelers, banks, quick-commerce | ~110 deals × ₹30 L average, across 8–10 festivals in 10+ cities | **₹33 cr** |
| **Footfall and OOH measurement** (did people actually pass your hoarding or stall, by hour?) | Brands, media agencies, OOH companies | ~60 clients × ₹35 L per season | **₹21 cr** |
| **Festival operations software** (committee portal tiers; white-label for governments, tourism, police and large organisers) | Committees, organisers, governments | ~3,000 committees × ₹25 k = ₹7.5 cr, plus ~12 institutional contracts × ₹60 L = ₹7.2 cr | **₹15 cr** |
| **Transactions** (passes, walks, slots, food pre-orders, travel affiliates) | Visitors, through partners | ~₹180 cr of bookings × ~12 % take rate | **₹21 cr** |
| **Guide-page ads and content licensing** | Ad networks, publishers (the embeddable quiet-hours widget, then its API) | High-traffic evergreen pages in 3–4 languages | **₹10 cr** |
| **Total** | | | **₹100 cr** |

**What it implies (assumptions):**
* **Reach:** about 2–3 crore unique users a year across festivals, with 50 lakh+ on peak nights.
* **Footfall data:** check-ins and crowd reports in the tens of lakhs.
* **Sales:** a 25–40-person sales and partnerships team.
* **Costs and capital:** gross margin of about 60–70 % with ad and data revenue mostly software margin and transactions thinner. Plausibly ₹60–90 crore of costs that year, so the target needs outside capital first.

## 3. The path, festival by festival

### Phase 1: Prove someone pays (Nov 2026 – Mar 2027)

| By | What | Exit test |
|---|---|---|
| Dec 2026 | Register a **private limited company**, the vehicle investors need. Set up a bank account, GST and a UPI/Razorpay link | Company registered |
| Dec 2026 | **Footfall reports (M5)** to every committee we have data on, free, as the hook | ≥30 committees receive one |
| Jan 2027 | **Media kit v1** with real 2026 numbers. Pitch the brands that built their own 2026 apps (Titan, Sunrise, Swiggy) on a cheaper white-label or sponsorship for 2027 | ≥10 brand meetings |
| Feb 2027 | **Committee portal pilot (M6)**: claim your pandal, post the 2027 theme, see last year's footfall | ≥50 committees claimed |
| Mar 2027 | **Saraswati Puja and the Book Fair** on the same engine (the multi-festival test) | Engine runs a second event with < 2 weeks of work |
| Mar 2027 | **Angel/pre-seed round: ₹1.5–3 crore** on LOIs and the data story. Pay for a founding team of 5–8 (engineering, data, sales, city partnerships) | Signed LOIs worth ≥₹50 L for Pujo 2027 |

### Phase 2: Win Kolkata and go multi-city (Apr – Nov 2027)

| By | What | Exit test |
|---|---|---|
| Apr 2027 | **Generalised engine (M7)**: venue, event days and a city pack, with one data folder per event. Add a Hindi-first UI for non-Bengal festivals | A new city pack in ≤10 days |
| Jun 2027 | **Sell Pujo 2027 by 1 June**, while brands set pujo budgets: a title sponsor, 5–10 brand partners and 100+ featured eateries | **₹1.5–2.5 cr booked** |
| Jul 2027 | Start pujo search, the WhatsApp Channel and committee onboarding in July, not October. Onboard Delhi-NCR (CR Park) and Bengaluru pujas | 300+ committees claimed |
| Sep 2027 | **Mumbai Ganesh pilot**: queue times and darshan routes | Proof of a city outside Bengal |
| Oct 2027 | **Pujo 2027 in 3 cities.** Crowd reports on, measurement reports for every paying brand, passes and walks bookable | **≥10 lakh users, ≥1 lakh verified check-ins, ≥₹3 cr revenue in FY 27-28** |
| Nov 2027 | **Series A: ₹25–50 crore**, raised on Pujo 2027 numbers. Only raise if the October tests passed (see §5) | Term sheet |

### Phase 3: The national festival calendar (Dec 2027 – Mar 2029)

| Window | Festivals and cities | Money |
|---|---|---|
| Dec 2027 – Mar 2028 | Christmas (Park Street, Bengaluru), the Book Fair, Saraswati Puja, Holi, Shivratri | Committee and organiser SaaS sales season; **the first 3–5 government or tourism white-label contracts** |
| Apr – Jun 2028 | Poila Baisakh, Rath Yatra (Puri, Kolkata), Thrissur Pooram; **the 2028 brand sales season** | **₹30–40 cr of brand deals booked by July** for the Aug–Nov window |
| Aug – Nov 2028 | Ganesh (Mumbai and Pune), Navratri garba (Gujarat), Durga Puja (6+ cities), Mysuru Dasara, Diwali, Chhath, Kali Puja and Jagaddhatri | **The peak quarter: 60–70 % of FY 28-29 revenue** |
| Dec 2028 – Mar 2029 | Christmas and New Year, Kumbh-style melas where organisers partner with us, plus renewals | Measurement and SaaS renewals; transactions all year |

**Revenue path (assumptions):**

| Year | Revenue | Main source |
|---|---|---|
| FY 26-27 | ₹0.1–0.3 cr | Featured offers, footfall reports, first sponsors |
| FY 27-28 | ₹3–5 cr | Pujo 2027 in 3 cities |
| FY 28-29 | **₹100 cr** (A) or **₹15–25 cr** (B) | National calendar |

The jump from FY 27-28 to FY 28-29 is the crux. It's only believable with Series A money, about 100 people, and two or three large anchor contracts: a state tourism board, a national FMCG brand across all festivals, and an OOH network.

### Faster routes to look at (inorganic)

* **Merge with or acquire a committee platform** such as Utsav (500+ committees, online dakshina). That brings the committee side and transactions at once.
* **A strategic partnership or sale** to a food-delivery, ticketing, maps, telecom or media company that wants festival-season engagement. Swiggy ran ShresthoPujo, and others build one-season campaign apps. This is the most likely route to outcome B.
* **A government partnership:** a statewide "festival crowd guide" contract (police and tourism) gives distribution we can't buy.

## 4. What has to be built (product and tech)

| When | Build | Why |
|---|---|---|
| Q4 2026 | Footfall report generator (M5), media kit page (M9), crowd reports (shipped 22 Nov), error monitoring (shipped 22 Nov) | Proof and sales assets |
| Q1 2027 | Committee portal (M6) with phone verification; payments (UPI/Razorpay); a Sponsored placement manager with an audit log showing paid slots never touched crowd advice | B2B revenue and trust |
| Q2 2027 | Multi-festival, multi-city engine (M7); a Hindi-first UI; the embeddable quiet-hours widget | Scale with a small team |
| Q3 2027 | Measurement product: geofenced footfall by hour around a brand's stalls and hoardings, with consented, aggregate-only data and a minimum group size before any number is shown | The B2B data line |
| 2028 | White-label guide (theming, own domain, organiser console); a bookings layer (passes, walks, slots); a data warehouse and a self-serve brand dashboard | SaaS, transactions and enterprise sales |
| Always | **Data accuracy first:** ground- or Google-verified pins before any city launch. Show less rather than show it wrong | The owner's top rule: people won't use the app if the data is wrong |

**Hosting and backend:** GitHub Pages and Supabase free tiers won't carry crores of users or enterprise contracts. Budget for a paid Supabase or Postgres tier, a CDN, an SLA and a DPDP-compliant consent and data setup from Pujo 2027. That's an owner decision with a cost.

## 5. Gates: when to push and when to switch goals

| Gate | Date | Push on towards A if… | Otherwise… |
|---|---|---|---|
| G1 | 31 Mar 2027 | ≥₹50 L of LOIs for Pujo 2027, ≥50 committees claimed, company and pre-seed done | Stay a profitable Bengal festival brand. Target B through a strategic sale |
| G2 | 30 Jun 2027 | ≥₹1.5 cr booked for Pujo 2027 | Cut the multi-city work and win Kolkata only |
| G3 | 15 Nov 2027 | ≥10 lakh users, ≥1 lakh check-ins, ≥₹3 cr FY 27-28 revenue, Series A term sheet | **Switch the goal to B** (₹100 cr valuation) and raise smaller or sell |
| G4 | 31 Jul 2028 | ≥₹40 cr contracted for Aug–Nov 2028 | Revise the FY 28-29 target honestly and protect cash |
| G5 | 31 Mar 2029 | ₹100 cr revenue | — |

## 6. Numbers to fill in now (owner)

| Metric | Pujo 2026 actual | Where to find it |
|---|---|---|
| Unique devices, 1–21 Oct | _fill in_ | `marketing-report` / `analytics-report` workflow output |
| Verified check-ins | _fill in_ | `analytics` schema in Supabase |
| WhatsApp Channel followers | _fill in_ | WhatsApp |
| Instagram followers / best reach | _fill in_ / 20,353 views | Instagram insights |
| Organic search clicks, Oct | _fill in_ | Search Console |
| Revenue | ₹0 | — |

## 7. Decisions needed from the owner

1. **Which reading of ₹100 crore is the goal: revenue (A) or valuation (B)?** This plan assumes A, gated, with B as the floor.
2. **Is this now a full-time business?** It needs a company, a co-founder or two (sales and engineering), and outside capital by March 2027.
3. **What money goes in before the angel round?** This covers the company, a paid backend and a Google Maps key for pins, roughly ₹1–3 lakh. Every one of these was a "don't spend without asking" item.
4. **Is a strategic or inorganic route acceptable** (merging with a committee platform, partnering with a large consumer app or a state government)?
5. **Confirm the non-negotiables:** paid placements never change crowd advice, no personal data sold, and aggregate-only data products.
