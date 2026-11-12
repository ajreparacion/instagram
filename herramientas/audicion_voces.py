#!/usr/bin/env python3
"""Audición de voces (12/11/2026, queja del dueño: «suena a lata, dice jaces por haces y le falta énfasis: que provoquen
la reacción, sea cual sea»). Genera las MISMAS frases con varias voces candidatas, las deja a la misma sonoridad
(-16 LUFS) y las sube a la release «pruebas» para que el dueño elija de oído. No publica nada.

Uso (workflow audicion_voces.yml):  python3 herramientas/audicion_voces.py [variantes separadas por comas]
Variantes:
  edge_*        voces neuronales de Microsoft (es-ES) por la librería edge-tts. OJO: es el servicio de lectura en voz alta
                de Edge, sin contrato: vale para ESCUCHAR la voz. Para producir con ella hay que usar la misma voz por
                Azure Speech con clave propia del dueño (nivel gratuito) o confirmar antes las condiciones.
  cb_es         Chatterbox afinado es-es con su voz integrada (sin referencia clonada), muy expresivo, sin h aspirada.
  cb_mtl        Chatterbox multilingüe con su voz integrada.
"""
import asyncio, json, os, subprocess, sys

SAL = "/tmp/audicion/salida"
FRASES = ["¿Tu cliente te paga a noventa días?",
          "Haces el presupuesto al momento, lo conviertes en pedido con un clic, y le envías el enlace de pago.",
          "Pide tu prueba gratuita: sin tarjeta, sin datos bancarios y sin compromiso."]
EDGE = {"edge_alvaro": ("es-ES-AlvaroNeural", "+6%", "+0Hz"), "edge_elvira": ("es-ES-ElviraNeural", "+6%", "+0Hz"),
        "edge_ximena": ("es-ES-XimenaNeural", "+6%", "+0Hz"), "edge_alvaro_energico": ("es-ES-AlvaroNeural", "+12%", "+6Hz")}
CB = {"cb_es": {"modelo": "es-es"}, "cb_mtl": {"modelo": "multilingue"}}


def master(entradas, salida):
    """Une las frases con 0,35 s de pausa y deja el conjunto a -16 LUFS / -1,5 dBTP."""
    args, filtro = [], ""
    for i, e in enumerate(entradas):
        args += ["-i", e]
        filtro += f"[{i}:a]aresample=48000,aformat=channel_layouts=mono,apad=pad_dur=0.35[a{i}];"
    filtro += "".join(f"[a{i}]" for i in range(len(entradas))) + f"concat=n={len(entradas)}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11[o]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args, "-filter_complex", filtro, "-map", "[o]", "-ar", "48000", "-ac", "2",
                    "-c:a", "libmp3lame", "-b:a", "192k", salida], check=True)


async def edge(nombre, voz, ritmo, tono):
    import edge_tts
    partes = []
    for i, f in enumerate(FRASES):
        p = f"/tmp/audicion/{nombre}_{i}.mp3"
        await edge_tts.Communicate(f, voz, rate=ritmo, pitch=tono).save(p)
        partes.append(p)
    master(partes, f"{SAL}/audicion_{nombre}.mp3")


def chatterbox(nombre, cfg):
    py = os.environ.get("PYTHON_CHATTERBOX") or sys.executable
    frases = [{"texto": f, "salida": f"/tmp/audicion/{nombre}_{i}.wav", **({"exageracion": 1.0, "cfg": 0.25} if i == 0 else {})}
              for i, f in enumerate(FRASES)]
    lote = {"modelo": cfg["modelo"], "idioma": "es", "exageracion": 0.85, "cfg": 0.3, "temperatura": 0.8, "referencia": None,
            "semilla": 7, "theta": "griego_sin_inicial", "frases": frases}
    r = f"/tmp/audicion/{nombre}.json"
    json.dump(lote, open(r, "w"), ensure_ascii=False)
    out = subprocess.run([py, os.path.join(os.path.dirname(os.path.abspath(__file__)), "voz_chatterbox.py"), r], capture_output=True, text=True)
    print(nombre, out.stdout[-600:], out.stderr[-400:], flush=True)
    if out.returncode == 0:
        master([f["salida"] for f in frases], f"{SAL}/audicion_{nombre}.mp3")


def main():
    os.makedirs(SAL, exist_ok=True)
    pedidas = [v.strip() for v in (sys.argv[1] if len(sys.argv) > 1 else "").split(",") if v.strip()] or list(EDGE) + list(CB)
    try:
        import edge_tts
        voces = asyncio.run(edge_tts.list_voices())
        print("voces es-ES de Edge:", [v["ShortName"] for v in voces if v["ShortName"].startswith("es-ES")], flush=True)
    except Exception as e:
        print("edge-tts no disponible:", str(e)[-200:], flush=True)
    for v in pedidas:
        try:
            if v in EDGE:
                asyncio.run(edge(v, *EDGE[v]))
            elif v in CB:
                chatterbox(v, CB[v])
            else:
                print("variante desconocida:", v)
                continue
            print("HECHA", v, flush=True)
        except Exception as e:
            print("FALLO", v, str(e)[-300:], flush=True)
    print("ficheros:", sorted(os.listdir(SAL)))


if __name__ == "__main__":
    main()
