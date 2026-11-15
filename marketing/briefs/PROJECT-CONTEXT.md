# Project context: Pujo Parikrama → a pan-India spiritual storytelling page

*As of 15 Nov 2026. Written so a person or another AI can pick up the work cold.*

---

## 1. What this is, in one paragraph

The project has two phases.

**Phase 1 (Sep–Oct 2026).** **Pujo Parikrama** was a free, mobile-first web app for Kolkata Durga Puja pandal hopping (https://pujoparikramaguide.in). Its Instagram page posted daily during the pujas (17–21 Oct 2026).

**Phase 2 (from 1 Nov 2026).** The pujas are over, so the Instagram page is pivoting to a **pan-India page of insightful, emotional stories about Hindu gods**. Every story aims for spirituality, hope and guidance for life. The page name is still to be decided; the owner rejected "Ko Jagarti". The north star is:

> Build a content calendar, a content production engine and engagement-optimised content that scale the page to organic engagement and **millions of monthly views**, then **monetise through brand deals**.

---

## 2. Phase 1 recap: the Durga Puja guide (done)

**Repo:** `iBiplavDas/Durga-Puja-2026` (renamed from `shubhgptgrowth/Durga-Puja-2026` in Nov 2026; old URLs redirect). It's **public**, so never commit phone numbers, payment details or contact lists, or pass them in workflow inputs.

**The app** is a static PWA in vanilla JS, served by GitHub Pages from branch `claude/kolkata-durga-puja-guide-4t5xad` on the custom domain pujoparikramaguide.in. It covered:
- 96 pandals in 5 regions;
- walking routes from Metro stations;
- food, parking and transit;
- live crowd-sourced check-ins (Supabase);
- photo moments, a step tracker and badges;
- English, Bengali and Hindi.

**Data pipeline:** `data/raw/*.csv` → `python -m pipeline` → `app/data/guide.json`.

**Marketing machinery that's still in use:**
- `marketing/`: the daily kit, caption rules, `publish_batch.py`.
- `.github/workflows/marketing-batch.yml`: posts to Instagram through the official Graph API, using repo secrets `IG_USER_ID` and `IG_ACCESS_TOKEN`.
- `engage.yml`: stats.
- Many other workflows for reels, audio, analytics and so on.

**After Dashami:** Home shows a "See you at Pujo 2027" WhatsApp reminder sign-up (consented list, stored in Supabase, never in the repo).

---

## 3. Audience and positioning (Phase 2)

- **Who:** Hindi-speaking teens and adults, **16–40**, across India. **Not kids.**
- **They respond to:** epic, emotional, spiritual stories that make them feel hopeful, give them a lesson for life, and make them want to share.
- **Inspiration pages:** spirituality and hope pages; Veda Story-style animation; **The Lost Puranas** (see §6).
- **Language:**
  - Narration and on-screen text: Hindi-first.
  - Captions: an English body for search, with a Hindi hook line.
  - The page used to be English and Bengali (Kolkata), but the audience is now all of India.

---

## 4. Non-negotiable rules

**Brand and ethics:**
- Every paid post is labelled **Sponsored**. A sponsor never changes a story, crowd advice, a route or a ranking.
- No fear or bad-luck threats ("share or else…"). No "type Jai if you're a true devotee" bait.
- No politics. Never put down another religion.
- **Cite the source** (Purana, Ramayana, Mahabharata…) in the caption.
- **AI disclosure** in the caption when visuals or voice are AI-made.
- **Credit** CC-licensed photos, footage and music, by photographer or musician plus licence.
- Respectful portrayal of deities. For difficult forms (such as Shiva in battle) use a silhouette rather than a close-up face.
- No founder name or quotes in press or posts without the owner's approval.

**Operations:**
- **Nothing posts without the owner's explicit approval of that specific reel.** Approved dates go in `marketing/daily/approved.txt`; never add one on your own.
- **No paid boosting.** **Monetisation stays off** until the owner approves.
- Merges to the default branch need a go-ahead for each PR. A direct request for a specific change counts.
- Each Claude session develops on its own `claude/*` branch. The default (deploy) branch is `claude/kolkata-durga-puja-guide-4t5xad`. The story-reel session's branch is `claude/nifty-dijkstra-iaamrp`; the briefs and the edit kit were pushed there first.

---

## 5. How the owner's taste has evolved

| When | Feedback | What changed |
|---|---|---|
| Early Nov | "Nobody wants to read so much text over images" | Moved from text carousels to visual storytelling |
| Early Nov | Wants animation like a Veda Story YouTube reference | Built an animation kit: layered parallax, cut-outs, glow, particles |
| 1 Nov | Loved the **3D storybook** Ganesha and Kartikeya reel ("fantastic") | Posted it, the first story reel |
| 11 Nov | "More realistic with effects, a voiceover that sounds like a real human, for teens and adults, not kids" | Moved to realistic and cinematic. Synthetic TTS (Kokoro) was rejected as not human enough |
| 14 Nov | Doesn't like the photo-montage style of the Chhath and Jagaddhatri reels | Every new reel must be **cinematic**, not photos with camera moves |
| 15 Nov | Shared The Lost Puranas' Jaya-Vijaya reel as the quality reference | The bar is now **story depth**, not just looks (see §6) |

---

## 6. The quality bar: what the reference reel taught us

The Lost Puranas' "Jaya and Vijaya" reel got 700K likes and 2,000+ comments in two days. It runs 1:48. The full teardown is in `marketing/briefs/reference-teardown-lostpuranas-jaya-vijaya.md`.

1. **The hook is an emotional paradox or a "why"** ("Vishnu's greatest enemy… loved him").
2. **It's a full story arc in 60–110 s:** setup → mistake → consequence → choice → payoff → **cliffhanger** ("Whose was the third birth? Follow, that is the next story"). Something new happens every 10–15 s.
3. **On-screen captions are synced word by word,** 2–4 words at a time, always in the same spot, with one key word in an accent colour. The reel works with sound off.
4. **It has one ownable visual world:** a recurring set, a palette, and motifs like the moon always at top right and patterned clouds. The animation is simple; the art direction and lighting carry the emotion (white for divine, red for curse).
5. **Abstract ideas get visual metaphors:** 7 gold stars for seven lives.
6. **It's a series by design,** so views turn into follows.

**Our rule from now on:** every reel gets a paradox or "why" hook, a complete arc, word-synced captions, a recurring look we own (not a copy of theirs), and a Part 2 cliffhanger.

---

## 7. The plans already made (private Claude artifacts)

- **Brand book:** https://claude.ai/artifact/Ses9DEYdvprQvieCWfCozG
- **Content Engine Plan (tools and costs):** https://claude.ai/artifact/LwTEbV91zVKtVRkhG1z1A8
- **Page Growth Plan** (6-week calendar, 4 series, engagement rules, monetisation ladder): https://claude.ai/artifact/MfAdCUm56YNhZstTj3GVRe

**Monetisation ladder (from the growth plan):** organic growth first. Brand deals come only once reach is proven, always labelled, and never touching a story.

---

## 8. The production engine

**Video generation options:**

| Route | What it gives | Limits and cost |
|---|---|---|
| **Google Flow** (owner generates) | Realistic cinematic clips (Omni Flash / Veo 3.1 Fast), 4–8 s each, 9:16 | Google AI Pro is about ₹1,950/month; about 12 credits per 8 s clip; 50 free credits a day. Not subscribed yet; the owner is testing |
| **Canva create-video** (Seedance) | Up to 30 s, 720p, with Hindi voice-over, from a shot-by-shot spec | The monthly AI limit ran out; it resets **Tue 17 Nov**. Each new video needs a new request from the owner |
| **Canva generate-image** | Still frames (3D storybook look) | Same monthly limit |
| **Higgsfield** | Kling, Seedance, Veo and others | Balance is about 0 credits |
| **Kling API / Gemini Omni API** | Pay per second | About $0.08–0.15 per second (in the Content Engine Plan) |

Sora is shut down, and CapCut isn't available in India.

**Voice:**
- Kokoro TTS was rejected.
- Options now: the owner records the narration themselves, Google AI Studio "Generate speech", or Sarvam Bulbul (about ₹30 per 10k characters).

**In-house edit kit** (Python + ffmpeg, in `marketing/engine/`; see its README):
- rembg cut-outs and OpenCV inpainting;
- layered parallax, breathing, clouds, glow, rays and particles;
- title overlays (Tiro Devanagari Sanskrit + Poppins);
- xfade edits, then a limiter and loudnorm to −16 LUFS.

**Photo-reel engine** (`marketing/engine/fest/make_fest.py`): Wikimedia Commons CC photos with camera moves and effects. The owner now dislikes this style; it's a fallback only.

**Workflow for a cinematic reel:**
1. Write the story in Hindi using the §6 structure.
2. Write a Flow prompt for each shot, plus a style line and the narration.
3. The owner generates the clips and the voice.
4. I edit: cuts timed to the voice, word-synced captions, score, end card.
5. The owner approves.
6. Post.

---

## 9. Posting pipeline

1. Put the MP4 in `app/media/reels/` on the default branch. It must be live at `https://pujoparikramaguide.in/media/reels/<file>.mp4` for Instagram to fetch it.
2. Add the posting file `marketing/batches/<date>-story-<slug>.json` (`{"note", "items":[{"type":"reel","id","video_url","caption"}]}`).
3. Add the date to `marketing/daily/approved.txt`, but **only after the owner approves**.
4. Open a PR to `claude/kolkata-durga-puja-guide-4t5xad`, merge, and wait for the deploy.
5. Post: dispatch **marketing-batch.yml** with `{"date":"","manifest":"<path>","start":"1","count":"0","gap":"300","dry_run":"false"}`. The log prints `→ media <id>`.

**Who posts what:**
- **Story-reel routine**, in this session: Tue/Thu/Sun at **7:27 pm IST**. It posts that day's approved `D-story-*.json`.
- **Weekly stats:** Monday at 10:13 IST (`engage.yml` in stats mode).
- **A separate "daily posting" Claude session** posts its own approved daily reels at about 9:30 pm IST. The two sessions tell each other what they posted so nothing goes up twice.

---

## 10. What's been posted and what's coming

| Date | Reel | Status |
|---|---|---|
| 1 Nov | Ganesha and Kartikeya's race (3D storybook, animated, 77 s) | Posted |
| 14 Nov | Chhath Puja (CC photo reel, 26 s) | Posted, media 18180919609463027 |
| 15 Nov, 11:43 am | Hanuman forgets his strength (3D storybook, 63 s) | Scheduled; the owner approved |
| 15 Nov, 7:27 pm | Jagaddhatri Puja (CC photo reel, 20 s) | Scheduled; the owner approved |
| 16 and 18 Nov | Chandannagar light artists / "Chandannagar this week" | The daily posting session handles these |
| **24 Nov (Tue)** | **Dev Deepawali, cinematic story version (about 70 s, 12 shots)** | Waiting on the owner's Flow clips and narration, needed by about **Fri 20 Nov** |

**Dev Deepawali story (Shiva Purana):**
1. **Hook:** "an asura so strong, the whole universe had to become a weapon to kill him".
2. **Brahma's boon:** the three flying cities fall only to one arrow, when all three line up, which happens once in 1,000 years.
3. **The gods build the cosmic chariot:** the earth as its body, the sun and moon as wheels, Brahma driving. Mount Meru is the bow, Vasuki the string, and Vishnu becomes the arrow.
4. **The alignment and the single arrow.**
5. **The gods light lamps in Kashi:** Dev Deepawali, 15 days after Diwali.
6. **Cliffhanger:** "why do the gods bathe in the Ganga that night? Next story."

Prompts: `marketing/briefs/2026-11-24-dev-deepawali-flow-prompts.md`. **The posting file for 24 Nov doesn't exist yet**; it's made after the edit is approved. The 30 s Canva spec is `marketing/briefs/2026-11-24-dev-deepawali-cinematic.json`, a backup used only if the owner says yes.

**Verified festival dates ahead:**
- Vivah Panchami: 14 Dec
- Gita Jayanti: 20 Dec
- Datta Jayanti: 23 Dec

**Story backlog:**
- Krishna and Sudama (2 storybook frames already made).
- A cinematic Hanuman (Flow prompts: `marketing/briefs/hanuman-cinematic-flow-prompts.md`).
- Neelkanth (Shiva drinking the poison; made earlier, in the storybook style).

---

## 11. Open decisions for the owner

1. **The page name.** "Ko Jagarti" was rejected.
2. **The signature visual style:**
   - cinematic realistic (Flow), or
   - an illustrated or cut-out "story world" like the reference (cheaper and more consistent), or
   - run both for two weeks and let the numbers decide (recommended).
3. **The tool budget:** Google AI Pro, or a pay-per-second API (Content Engine Plan).
4. **Monetisation:** off until approved.

---

## 12. Where things live

**In the repo:**
- `marketing/briefs/`: the Dev Deepawali prompt sheet and the Canva backup spec.
- `marketing/batches/`: posting files.
- `marketing/daily/approved.txt`: the owner-approved posting dates.
- `marketing/voice.md`: the Phase 1 Bengali voice, still used for the pujo posts.
- `marketing/voice-stories.md`: **the Phase 2 Hindi story voice (draft, for the owner to review)**.
- `marketing/engine/`: the reel edit kit.
- `marketing/briefs/`: Flow prompt sheets, the Canva backup spec, the reference teardown, and this file.
- `docs/marketing/PLAN.md`: the Phase 1 playbook.
- `app/media/reels/`: the posted videos.

Rendered reels that were never posted (for example drafts) lived only in a session scratchpad and may be gone. Posted reels are in `app/media/reels/`.
