#!/usr/bin/env python3
"""ElevenLabs narration for the story reels, with word timings for the captions.

Needs the environment variable ELEVENLABS_API_KEY (an environment secret, never committed).
Standard library only.

  # find a deep male Hindi storyteller voice in the shared library
  python3 elevenlabs.py voices --shared --lang hi
  # list voices already in the account
  python3 elevenlabs.py voices
  # add a shared voice to the account (needed before using it)
  python3 elevenlabs.py add PUBLIC_OWNER_ID VOICE_ID "Narrator"
  # narrate a script: writes vo.mp3 plus words.json (start/end in seconds for each word)
  python3 elevenlabs.py say script.txt VOICE_ID /tmp/reel-work/devdeep/vo

Each line of script.txt is one beat. The lines are sent as one take, so the voice flows
naturally, with a pause between lines. words.json drives the word-by-word captions in the edit.
"""
import base64, json, os, sys, urllib.parse, urllib.request

API = "https://api.elevenlabs.io/v1"
MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")  # handles Hindi
# Slow, steady storyteller: a little variation, no theatrics.
SETTINGS = {"stability": 0.55, "similarity_boost": 0.8, "style": 0.25, "use_speaker_boost": True}


def call(method, path, body=None):
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("ELEVENLABS_API_KEY is not set. Add it as an environment secret and start a new session.")
    req = urllib.request.Request(API + path, method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"xi-api-key": key, "Content-Type": "application/json",
                                          "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs {e.code}: {e.read().decode()[:400]}")


def voices(args):
    if "--shared" in args:
        lang = args[args.index("--lang") + 1] if "--lang" in args else "hi"
        q = urllib.parse.urlencode({"language": lang, "gender": "male", "page_size": 30,
                                    "category": "professional", "sort": "usage_character_count_1y"})
        for v in call("GET", f"/shared-voices?{q}").get("voices", []):
            print(f"{v['voice_id']}  owner={v.get('public_owner_id')}  {v.get('name')} · "
                  f"{v.get('age', '')} {v.get('accent', '')} · {(v.get('description') or '')[:70]}")
    else:
        for v in call("GET", "/voices").get("voices", []):
            print(f"{v['voice_id']}  {v['name']}  {v.get('labels', {})}")


def add(args):
    owner, vid, name = args[0], args[1], args[2]
    print(call("POST", f"/voices/add/{owner}/{vid}", {"new_name": name}))


def words_from(al):
    """Group the character timings into words (split on whitespace)."""
    out, cur, start, end = [], "", None, None
    for ch, s, e in zip(al["characters"], al["character_start_times_seconds"],
                        al["character_end_times_seconds"]):
        if ch.isspace():
            if cur:
                out.append({"w": cur, "start": round(start, 3), "end": round(end, 3)})
            cur, start = "", None
            continue
        if start is None:
            start = s
        cur, end = cur + ch, e
    if cur:
        out.append({"w": cur, "start": round(start, 3), "end": round(end, 3)})
    return out


def say(args):
    script, vid, outdir = args[0], args[1], args[2]
    lines = [l.strip() for l in open(script, encoding="utf-8") if l.strip()]
    text = "\n\n".join(lines)  # blank line between beats gives a natural pause
    r = call("POST", f"/text-to-speech/{vid}/with-timestamps?output_format=mp3_44100_192",
             {"text": text, "model_id": MODEL, "voice_settings": SETTINGS})
    os.makedirs(outdir, exist_ok=True)
    open(os.path.join(outdir, "vo.mp3"), "wb").write(base64.b64decode(r["audio_base64"]))
    words = words_from(r.get("normalized_alignment") or r["alignment"])
    json.dump(words, open(os.path.join(outdir, "words.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"vo.mp3 + {len(words)} timed words → {outdir} (ends at {words[-1]['end']:.1f}s)")


if __name__ == "__main__":
    cmd, rest = (sys.argv[1], sys.argv[2:]) if len(sys.argv) > 1 else ("", [])
    {"voices": voices, "add": add, "say": say}.get(cmd, lambda a: sys.exit(__doc__))(rest)
