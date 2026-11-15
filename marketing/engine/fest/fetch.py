import json, sys, time, urllib.request
UA = {"User-Agent": "PujoParikramaGuide/1.0 (https://pujoparikramaguide.in; reels with credits)"}
tag, picks = sys.argv[1], [int(x) for x in sys.argv[2].split(",")]
rows = json.load(open(f"{tag}_rows.json")); credits = []
for i in picks:
    r = rows[i]
    u = r["thumb"].replace("/1600px-", "/2560px-") if max(r["w"], r["h"]) > 2560 else r["full"]
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as resp:
                open(f"hi/{tag}_{i}.jpg", "wb").write(resp.read()); break
        except Exception as e:
            print("retry", i, e); time.sleep(10 * (attempt + 1))
    credits.append({"i": i, "title": r["title"][5:], "artist": r["artist"], "lic": r["lic"]})
    time.sleep(3)
json.dump(credits, open(f"{tag}_credits.json", "w"), ensure_ascii=False, indent=1); print(tag, "done")
