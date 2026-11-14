#!/usr/bin/env python3
"""Locución con edge-tts (voces neuronales de Microsoft Edge, gratis, es-ES). DIRECTIVA DE VÍDEO 14/11/2026.
Una voz por personaje: jambo = es-ES-AlvaroNeural (--rate=+6% --pitch=-3Hz), jupillo = es-ES-XimenaNeural,
resto de IAs y narración = es-ES-ElviraNeural. Nunca la voz del dueño.
Cadena por frase (un archivo por frase): silenceremove a -45 dB, aresample 48000, highpass 70 Hz, compresor 2,5:1 a -20 dB
(ataque 8 ms, suelta 120 ms), +2 dB en 3,5 kHz; sin reverb ni paso bajo.
Uso: python3 voz_edge.py lote.json  (lote = {"voces": {...}, "frases": [{"texto","salida","hablante"}]}). Sale != 0 si falla."""
import asyncio, json, os, subprocess, sys, tempfile, time

VOCES = {
    "jambo": {"voz": "es-ES-AlvaroNeural", "rate": "+6%", "pitch": "-3Hz"},
    "jupillo": {"voz": "es-ES-XimenaNeural", "rate": "+0%", "pitch": "+0Hz"},
    "defecto": {"voz": "es-ES-ElviraNeural", "rate": "+0%", "pitch": "+0Hz"},
}
CADENA = ("silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_duration=0.25:stop_threshold=-45dB,"
          "aresample=48000,highpass=f=70,"
          "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=1,"
          "equalizer=f=3500:t=q:w=1:g=2")


def cfg_de(hablante, voces):
    c = dict(VOCES["defecto"])
    c.update(voces.get(hablante) or VOCES.get(hablante) or voces.get("defecto") or {})
    return c


async def una(texto, salida_mp3, c):
    import edge_tts
    last = None
    for intento in range(3):
        try:
            com = edge_tts.Communicate(texto, c["voz"], rate=c["rate"], pitch=c["pitch"])
            await com.save(salida_mp3)
            if os.path.exists(salida_mp3) and os.path.getsize(salida_mp3) > 800:
                return
        except Exception as e:
            last = e
        await asyncio.sleep(2 * (intento + 1))
    raise SystemExit(f"edge-tts falló para «{texto[:50]}»: {last}")


def main():
    lote = json.load(open(sys.argv[1], encoding="utf-8"))
    voces = lote.get("voces") or {}
    t0 = time.time()
    for f in lote["frases"]:
        c = cfg_de(f.get("hablante"), voces)
        mp3 = f["salida"] + ".mp3"
        asyncio.run(una(f["texto"], mp3, c))
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-af", CADENA, "-ar", "48000", "-ac", "1",
                            "-c:a", "pcm_s16le", f["salida"]], capture_output=True, text=True)
        os.remove(mp3)
        if r.returncode != 0 or not os.path.exists(f["salida"]) or os.path.getsize(f["salida"]) < 2000:
            raise SystemExit("ffmpeg falló en la cadena de voz: " + (r.stderr or "")[-200:])
    print(json.dumps({"modelo_usado": "edge-tts es-ES", "sr": 48000, "total_s": round(time.time() - t0, 1)}))


if __name__ == "__main__":
    main()
