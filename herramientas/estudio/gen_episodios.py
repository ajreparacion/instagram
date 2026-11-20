"""Genera los spec.json de Neogest Studio para episodios de El Jambo que sabe (reparto Rosa/Felipe/Sindy/
Concha Quetón/Neo). v5.1 (20/11/2026 noche, orden del dueño tras ver el piloto v1):
  - Bucle "Cosas de Casa": apertura y cierre usan el MISMO objeto de escena (misma tarjeta, mismo plano,
    sin texto distinto por episodio) para que el bucle sea imperceptible. Se usa en TODOS los episodios,
    no varía por hora/noche ni depende de "flow" (eso se reserva para b-roll real dentro del episodio si
    algún día hace falta). Mientras no haya un vídeo real de fachada de barrio, usa el set vectorial "casa".
  - Etiqueta de nombre y apellido: la dibuja engine.js en espacio de pantalla, fuera del zoom de cámara
    (antes se recortaba en los primeros planos; corregido 20/11 noche).
  - Más expresividad de voz: modulación de velocidad/tono por emoción de la escena (EXPR_MOD), sobre la
    base de cada personaje (VOZ).
  - Risas de sitcom: marca "risas: true" en una escena de gag para añadir el sfx "risas" al final de la
    réplica (biblioteca ya incluida en Neogest Studio, src/studio/library.js).
Uso (en el sandbox de Neogest Studio, Base44 6af862101565c330cf06389f):
  pip install edge-tts; python3 gen_episodios.py eps.json /tmp/jb
  node scripts/render.mjs /tmp/jb/<n>.json /tmp/jb/<n>.mp4 --hoja
eps.json: [{"slug","set","hora","moraleja","escenas":[{"e":gancho|gag|remate|cierre,"h":personaje,"v":voz,
"t":texto,"p":[personajes],"a":{personaje:accion},"sello","risas"}]}]
Humor negro real (biblia v5, guionista_gemini.py): tono frío, nunca sobre pobreza/enfermedad/muerte reales;
los personajes se llaman por su nombre entre ellos (registro de barrio con réplica inteligente).
"""
import json, asyncio, random, sys, edge_tts
EPS = json.load(open(sys.argv[1])); OUT = sys.argv[2]
# Vídeo real para "Cosas de Casa" (pedido en equipo/cola_gemini.md el 20/11: Gemini/Flow o,
# a mano, ChatGPT/Sora). En cuanto exista la URL pública, ponla aquí UNA vez y todos los
# episodios (presentes y futuros) pasan a usarla automáticamente; hasta entonces None = set
# vectorial "casa". No repetir el pedido por episodio.
COSAS_DE_CASA_VIDEO = "https://media.base44.com/videos/public/6af862101565c330cf06389f/4ae3afde4_cosas-de-casa-intro.mp4"
# voz base por personaje: (voz, rate% base, pitch Hz base)
VOZ = {"rosa": ("es-ES-ElviraNeural", 0, -4), "felipe": ("es-ES-AlvaroNeural", -4, -2), "sindy": ("es-ES-XimenaNeural", 8, 4),
       "neo": ("es-ES-AlvaroNeural", 0, 0), "cliente": ("es-ES-AlvaroNeural", -4, -10),
       "conchaqueton": ("es-ES-ElviraNeural", -6, 2), None: ("es-ES-ElviraNeural", 0, 0)}
# modulacion por emocion de la escena (orden del dueño 20/11 noche: mas expresividad)
EXPR_MOD = {"habla": (0, 0), "desespera": (18, 10), "delega": (-12, -8), "presume": (10, 6), "fria": (-8, -10)}
EXPR = {"habla": "neutral", "desespera": "enfadado", "delega": "cansado", "presume": "chulo", "fria": "neutral"}
EMO = ["😤", "🤯", "😱", "💸", "🙄", "😳"]
uid = lambda: "%08x" % random.getrandbits(32)

async def tts(text, who, path, emo="habla"):
    v, br, bp = VOZ[who]; mr, mp = EXPR_MOD.get(emo, (0, 0))
    r, p = f"{br+mr:+d}%", f"{bp+mp:+d}Hz"
    c = edge_tts.Communicate(text.replace("*", ""), v, rate=r, pitch=p, boundary="WordBoundary"); words = []
    with open(path, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                s = ch["offset"] / 1e7; words.append({"w": ch["text"].strip(".,;:¡!¿?"), "s": round(s, 3), "e": round(s + ch["duration"] / 1e7, 3)})
    return words

def bookend():
    # Plano de casa (estilo sitcom americano de los 90, "Cosas de Casa"/Full House, era solo referencia de
    # ESTILO para el dueño, nunca texto en pantalla -> corregido 20/11 noche, 4.ª pasada: sin overlay de texto).
    # Misma tarjeta EXACTA en apertura y cierre de todos los episodios (bucle imperceptible).
    bg = {"type": "video", "url": COSAS_DE_CASA_VIDEO, "start": 0.0} if COSAS_DE_CASA_VIDEO else {"type": "set", "set": "casa", "hour": 19, "night": False}
    return {"id": uid(), "duration": 1.6, "transition": "none", "voice": None, "background": bg, "texts": []}

async def main():
    for ep in EPS:
        n = ep["slug"][:3]; bg = {"type": "set", "set": ep["set"], "hour": ep["hora"], "night": ep["hora"] >= 21}; scenes = []
        vistos = set()  # para la etiqueta de nombre y apellido, solo en la primera aparición de cada personaje
        for i, e in enumerate(ep["escenas"]):
            emo = e["a"].get(e["h"], "habla") if e.get("a") else "habla"
            path = f"{OUT}/{n}_{i}.mp3"; words = await tts(e["v"], e["h"], path, emo); dur = (words[-1]["e"] if words else 1.0) + 0.05
            voice = {"text": e["v"], "provider": "edge", "speaker": e["h"] or "narrador", "url": path, "duration": dur, "words": words, "offset": 0.05, "tail": 0.12}
            if e["e"] == "cierre":
                cierre_cast = [{"who": "felipe", "x": 0.3, "expr": "cansado"}, {"who": "neo", "x": 0.72, "expr": "feliz"}]
                for cc in cierre_cast:
                    if cc["who"] not in vistos: cc["intro"] = True; vistos.add(cc["who"])
                scenes.append({"id": uid(), "duration": dur + 0.6, "transition": "zoom", "background": bg, "characters": cierre_cast, "shot": "general", "voice": voice,
                               "texts": [{"id": uid(), "text": ep["moraleja"], "style": "badge", "anim": "pop", "y": 0.12, "sfx": "impacto"}, {"id": uid(), "text": e["t"], "style": "hook", "anim": "pop", "start": 0.5, "y": 0.26}]}); continue
            p = e["p"] or [e["h"]]; xs = {}
            if "felipe" in p: xs["felipe"] = 0.3
            for w in p:
                if w not in xs: xs[w] = 0.72 if 0.72 not in xs.values() else 0.3
            cast = []
            for w in p[:2]:
                ex = EXPR.get(e["a"].get(w, "habla"), "neutral")
                if e["e"] == "remate": ex = "chulo" if w == e["h"] else "sorprendido"
                entry = {"who": w, "x": xs[w], "expr": ex}
                if w not in vistos: entry["intro"] = True; vistos.add(w)
                cast.append(entry)
            # BUG corregido 20/11 noche (4.ª pasada): la duración estaba fijada a 0.4s sin importar el audio real,
            # así que la escena cambiaba antes de que acabara el audio Y antes de que la etiqueta de nombre
            # (fade de 1.1s en engine.js) llegara a mostrarse. Ahora dura lo que dura el audio + margen.
            sc = {"id": uid(), "duration": dur + 0.35, "transition": "slide" if i else "none", "background": bg, "characters": cast, "voice": voice, "shot": ["auto", "medio", "primerplano", "auto", "general"][i % 5], "texts": []}
            if i >= 1 and e["e"] == "gag" and e["h"] != "neo":
                sc["overlays"] = [{"id": uid(), "type": "emoji", "text": EMO[i % len(EMO)], "x": 0.82 if xs.get(e["h"], 0.3) < 0.5 else 0.18, "y": 0.32, "start": 0.25, "size": 0.12}]
            if e["e"] == "remate": sc["shot"] = "primerplano"; sc["transition"] = "flash"
            if e.get("sello"): sc["texts"].append({"id": uid(), "text": e["sello"], "style": "badge", "anim": "pop", "start": 0.4, "y": 0.3, "sfx": "impacto"})
            if e.get("risas"): sc["texts"].append({"id": uid(), "text": "😂", "style": "badge", "anim": "pop", "start": max(0.1, dur * 0.55), "y": 0.08, "sfx": "risas"})
            scenes.append(sc)
        scenes.insert(0, bookend())
        scenes.append(bookend())
        spec = {"version": 1, "format": "9:16", "fps": 30, "music": {"track": "comedia:1", "volume": 0.16, "duck": True, "duckLevel": 0.3}, "subtitles": {"enabled": True, "words": 3, "style": "amarillo", "emojis": True, "size": 0.07},
                "brand": {"watermark": True, "watermarkPos": "right", "progress": True}, "sfx": {"enabled": True, "volume": 0.6}, "scenes": scenes}
        json.dump(spec, open(f"{OUT}/{n}.json", "w"), ensure_ascii=False); print(n, len(scenes), "escenas")

asyncio.run(main())
