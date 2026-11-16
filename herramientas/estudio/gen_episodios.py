"""Genera los spec.json de Neogest Studio para episodios de El Jambo que sabe (reparto Rosa/Felipe/Sindy/Neo, 16/11/2026).
Uso (en el sandbox de Neogest Studio, Base44 6af862101565c330cf06389f):
  pip install edge-tts; python3 gen_episodios.py eps.json /tmp/jb
  node scripts/render.mjs /tmp/jb/<n>.json /tmp/jb/<n>.mp4 --hoja
eps.json: [{"slug","set","hora","flow","moraleja","escenas":[{"e":gancho|gag|remate|cierre,"h":personaje,"v":voz,"t":texto,"p":[personajes],"a":{personaje:accion},"sello"}]}]
"""
import json, asyncio, random, sys, edge_tts
EPS = json.load(open(sys.argv[1])); OUT = sys.argv[2]
VOZ = {"rosa": ("es-ES-ElviraNeural", "+0%", "-4Hz"), "felipe": ("es-ES-AlvaroNeural", "-4%", "-2Hz"), "sindy": ("es-ES-XimenaNeural", "+8%", "+4Hz"),
       "neo": ("es-ES-AlvaroNeural", "+0%", "+0Hz"), "cliente": ("es-ES-AlvaroNeural", "-4%", "-10Hz"), None: ("es-ES-ElviraNeural", "+0%", "+0Hz")}
EXP = {"habla": "neutral", "desespera": "enfadado", "delega": "cansado", "presume": "chulo"}
EMO = ["😤", "🤯", "😱", "💸", "🙄", "😳"]
uid = lambda: "%08x" % random.getrandbits(32)

async def tts(text, who, path):
    v, r, p = VOZ[who]; c = edge_tts.Communicate(text.replace("*", ""), v, rate=r, pitch=p, boundary="WordBoundary"); words = []
    with open(path, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                s = ch["offset"] / 1e7; words.append({"w": ch["text"].strip(".,;:¡!¿?"), "s": round(s, 3), "e": round(s + ch["duration"] / 1e7, 3)})
    return words

async def main():
    for ep in EPS:
        n = ep["slug"][:3]; bg = {"type": "set", "set": ep["set"], "hour": ep["hora"], "night": ep["hora"] >= 21}; scenes = []
        for i, e in enumerate(ep["escenas"]):
            path = f"{OUT}/{n}_{i}.mp3"; words = await tts(e["v"], e["h"], path); dur = (words[-1]["e"] if words else 1.0) + 0.05
            voice = {"text": e["v"], "provider": "edge", "speaker": e["h"] or "narrador", "url": path, "duration": dur, "words": words, "offset": 0.05, "tail": 0.12}
            if e["e"] == "cierre":
                scenes.append({"id": uid(), "duration": dur + 0.6, "transition": "zoom", "background": bg, "characters": [{"who": "felipe", "x": 0.3, "expr": "cansado"}, {"who": "neo", "x": 0.72, "expr": "feliz"}], "shot": "general", "voice": voice,
                               "texts": [{"id": uid(), "text": ep["moraleja"], "style": "badge", "anim": "pop", "y": 0.12, "sfx": "impacto"}, {"id": uid(), "text": e["t"], "style": "hook", "anim": "pop", "start": 0.5, "y": 0.26}]}); continue
            p = e["p"] or [e["h"]]; xs = {}
            if "felipe" in p: xs["felipe"] = 0.3
            for w in p:
                if w not in xs: xs[w] = 0.72 if 0.72 not in xs.values() else 0.3
            cast = []
            for w in p[:2]:
                ex = EXP.get(e["a"].get(w, "habla"), "neutral")
                if e["e"] == "remate": ex = "chulo" if w == e["h"] else "sorprendido"
                cast.append({"who": w, "x": xs[w], "expr": ex})
            sc = {"id": uid(), "duration": 0.4, "transition": "slide" if i else "none", "background": bg, "characters": cast, "voice": voice, "shot": ["auto", "medio", "primerplano", "auto", "general"][i % 5], "texts": []}
            if i >= 1 and e["e"] == "gag" and e["h"] != "neo":
                sc["overlays"] = [{"id": uid(), "type": "emoji", "text": EMO[i % len(EMO)], "x": 0.82 if xs.get(e["h"], 0.3) < 0.5 else 0.18, "y": 0.32, "start": 0.25, "size": 0.12}]
            if e["e"] == "remate": sc["shot"] = "primerplano"; sc["transition"] = "flash"
            if e.get("sello"): sc["texts"].append({"id": uid(), "text": e["sello"], "style": "badge", "anim": "pop", "start": 0.4, "y": 0.3, "sfx": "impacto"})
            scenes.append(sc)
        scenes.insert(0, {"id": uid(), "duration": 1.3, "transition": "none", "background": {"type": "video", "url": ep["flow"], "start": 1.0}, "texts": [{"id": uid(), "text": ep["escenas"][0]["t"], "style": "hook", "anim": "pop", "y": 0.45, "sfx": "whoosh"}], "voice": None})
        scenes.append({"id": uid(), "kind": "outro", "duration": 1.7, "transition": "zoom", "texts": [{"id": uid(), "text": "Síguenos para el próximo episodio", "style": "badge", "anim": "pop", "start": 0.6, "y": 0.72}]})
        spec = {"version": 1, "format": "9:16", "fps": 30, "music": {"track": "comedia:1", "volume": 0.16, "duck": True, "duckLevel": 0.3}, "subtitles": {"enabled": True, "words": 3, "style": "amarillo", "emojis": True, "size": 0.07},
                "brand": {"watermark": True, "watermarkPos": "right", "progress": True}, "sfx": {"enabled": True, "volume": 0.6}, "scenes": scenes}
        json.dump(spec, open(f"{OUT}/{n}.json", "w"), ensure_ascii=False); print(n, len(scenes), "escenas")

asyncio.run(main())
