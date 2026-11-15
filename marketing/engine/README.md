# Reel edit kit (Phase 2 story reels)

The Python and ffmpeg scripts used to make the story reels in Nov 2026. They were moved here from a session scratchpad so they survive container resets. Work files go in **`/tmp/reel-work`**, with fonts in `/tmp/reel-work/fonts`.

| File | What it does |
|---|---|
| `anim/brand.py` | Shared look: 1080×1920 at 30 fps, palette (NIGHT, GOLD, IVORY), fonts (Tiro Devanagari Sanskrit + Poppins), easing, tracked labels |
| `anim/make_anim.py` | The animation kit. Takes still frames (for example Canva 3D storybook art), cuts subjects out with rembg (isnet), inpaints the background with OpenCV, and animates layered parallax, breathing, rush clouds and wind, glow, rays and motes. Adds Devanagari titles and an xfade edit with narration. The limiter is `alimiter=limit=0.8:level=false,volume=-1.5dB`. `K.render()` writes the reel |
| `hanuman/make_hanuman.py` | Example reuse: sets `K.FR`, `K.VO`, `K.OUT` and `K.SHOTS` for the Hanuman storybook reel |
| `fest/make_fest.py` | The photo-reel engine (Chhath and Jagaddhatri, 14–15 Nov). Wikimedia Commons CC photos with camera moves, sun, diya and ember effects, grain, and bold Hindi and English titles. Run `python3 make_fest.py chhath\|jag [preview]`. **The owner dislikes this style, so use it only as a fallback** |
| `fest/pick.py`, `fest/fetch.py` | Search Wikimedia Commons, make contact sheets, and download full-size photos with credits. Use a User-Agent and sleeps, because the API rate-limits |
| `fest/*_credits.json` | Photographer and licence for each photo used in those reels |
| `vo/elevenlabs.py` | **The narration route the owner chose (15 Nov).** ElevenLabs text-to-speech with timestamps. It writes `vo.mp3` plus `words.json` (per-word start and end) for the word-synced captions, and can list and add Hindi voices from the shared library. Needs the `ELEVENLABS_API_KEY` environment secret. Run `python3 elevenlabs.py` for usage |
| `vo/lines.py` | Kokoro TTS (`hm_omega`, under python3.11). Args: lines.json, outdir, voice, speed. **The owner rejected synthetic TTS as not human enough**; use a real recording or Google AI Studio speech instead |

Dependencies: `pillow`, `numpy`, `opencv-python`, `rembg[cpu]` (isnet model), `ffmpeg`. Kokoro needs python3.11.

**Final-edit checklist:**
- loudnorm to `I=-16:TP=-1.5`;
- 1080×1920 H.264;
- check every frame on a contact sheet;
- write the caption with the `ig-caption` skill rules.
