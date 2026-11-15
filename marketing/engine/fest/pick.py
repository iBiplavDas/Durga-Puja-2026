import json, re, sys, time, urllib.request
from PIL import Image, ImageDraw
UA = {"User-Agent": "PujoParikramaGuide/1.0 (https://pujoparikramaguide.in; reels with credits)"}
f, tag = sys.argv[1], sys.argv[2]
d = json.load(open(f)); rows = []
for p in d["query"]["pages"].values():
    ii = p.get("imageinfo", [{}])[0]; m = ii.get("extmetadata", {})
    lic = m.get("LicenseShortName", {}).get("value", "")
    if ii.get("width", 0) * ii.get("height", 0) < 1500000 or not lic or "Route Map" in p["title"]:
        continue
    rows.append({"title": p["title"], "thumb": ii["thumburl"], "full": ii["url"], "lic": lic,
                 "artist": re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip(), "w": ii["width"], "h": ii["height"]})
json.dump(rows, open(f"{tag}_rows.json", "w"), ensure_ascii=False, indent=1)
tiles = []
for i, r in enumerate(rows):
    u = r["thumb"].replace("/1600px-", "/320px-")
    try:
        with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as resp:
            open(f"/tmp/reel-work/fest/t_{tag}_{i}.jpg", "wb").write(resp.read())
        im = Image.open(f"/tmp/reel-work/fest/t_{tag}_{i}.jpg").convert("RGB"); im.thumbnail((220, 220))
        tiles.append((i, im))
    except Exception as e:
        print("skip", i, e)
    time.sleep(0.4)
cols = 8; rows_n = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 230, rows_n * 240), "white"); dr = ImageDraw.Draw(sheet)
for k, (i, im) in enumerate(tiles):
    x, y = (k % cols) * 230, (k // cols) * 240
    sheet.paste(im, (x, y)); dr.text((x + 3, y + 222), str(i), fill=(200, 0, 0))
sheet.save(f"sheet_{tag}.jpg", quality=85); print(tag, len(tiles))
