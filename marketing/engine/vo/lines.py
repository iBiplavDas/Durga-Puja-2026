import sys, json, numpy as np, soundfile as sf
from kokoro import KPipeline
lines = json.load(open(sys.argv[1])); out = sys.argv[2]; voice = sys.argv[3]
p = KPipeline(lang_code='h')
d = {}
for k, text in lines.items():
    a = np.concatenate([x for _, _, x in p(text, voice=voice, speed=float(sys.argv[4]) if len(sys.argv) > 4 else 0.9)])
    sf.write(f"{out}/{k}.wav", a, 24000); d[k] = len(a) / 24000
json.dump(d, open(f"{out}/durations.json", "w"), indent=1); print(d)
