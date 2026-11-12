#!/usr/bin/env python3
"""Consulta la API de audio de Instagram (GET /ig_audio, Meta «Instagram Audio API»: audios autorizados para terceros).
Guarda en equipo/audios_instagram.json la respuesta cruda (tendencia + búsquedas por estilo) para elegir canciones.
Uso (lo lanza .github/workflows/audios_ig.yml, a mano): python3 herramientas/audios_ig.py ["consulta1,consulta2"]
No publica nada. Necesita PAGE_TOKEN (inicio de sesión de Facebook, permisos instagram_basic + instagram_content_publish)."""
import json
import os
import sys
import time

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
import publicar_gh as P  # noqa: E402

CONSULTAS = ["", "reggaeton", "dembow", "phonk", "house", "tech house", "upbeat", "energetic", "hip hop", "latin pop",
             "afrobeats", "instrumental", "motivational"]


def main():
    cfg = P.cargar_config()
    extra = [q.strip() for q in (sys.argv[1].split(",") if len(sys.argv) > 1 and sys.argv[1] else [])]
    informe = {"fecha": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "consultas": {}}
    for tipo in ("music", "original_sound"):
        for q in (extra or CONSULTAS):
            nombre = f"{tipo}:{q or 'tendencia'}"
            params = {"audio_type": tipo, "user_id": cfg["ig_user_id"]}
            if q:
                params["search_query"] = q
            try:
                r = P.api(cfg, "ig_audio", **params)
                datos = r.get("data", r)
                informe["consultas"][nombre] = {"n": len(datos) if isinstance(datos, list) else None, "respuesta": r,
                                                "paginas": bool((r.get("paging") or {}).get("next"))}
                print(f"{nombre}: {informe['consultas'][nombre]['n']} resultados", flush=True)
            except Exception as e:  # el error de la API es la información (permisos, país, etc.)
                informe["consultas"][nombre] = {"error": str(e)[:600]}
                print(f"{nombre}: ERROR {str(e)[:300]}", flush=True)
            if tipo == "original_sound":
                break   # un solo sondeo de sonidos originales (tendencia); no nos interesan para esta cuenta
    destino = os.path.join(BASE, "equipo", "audios_instagram.json")
    json.dump(informe, open(destino, "w", encoding="utf-8"), ensure_ascii=False, indent=1)




def probar(audio_id, asset=None, tipo="REELS"):
    """Crea un contenedor REELS (o STORIES) con audio_configuration desde la release (video_url) y mira si Instagram lo acepta.
    NO llama a media_publish: el contenedor caduca solo.
    Uso: python3 herramientas/audios_ig.py --probar AUDIO_ID [asset.mp4] [--historia]"""
    tipo = "STORIES" if str(tipo).upper().startswith("STOR") else "REELS"
    cfg = P.cargar_config()
    if not asset:
        repo = os.environ.get("GITHUB_REPOSITORY", "ajreparacion/instagram")
        r = P.gh("api", f"repos/{repo}/releases/tags/{P.RELEASE}", "-q", ".assets[].name")
        nombres = [x for x in r.stdout.split() if x.endswith(".mp4")]
        if tipo == "STORIES":   # mejor con un vídeo de historia de verdad (duración y formato de historia)
            nombres = [x for x in nombres if "historia" in x] or nombres
        if not nombres:
            print("sin .mp4 en la release de cola: no se puede probar"); return
        asset = nombres[0]
    params = {"media_type": tipo, "video_url": P.url_directa_release(asset),
              "audio_configuration": json.dumps({"audio_id": str(audio_id), "audio_volume": 0.8, "video_volume": 1.0})}
    if tipo == "REELS":
        params["caption"] = "(prueba de audio, no se publica)"
    print(f"prueba {tipo} con {asset} y audio_id {audio_id}", flush=True)
    try:
        r = P.api(cfg, f"{cfg['ig_user_id']}/media", "POST", **params)
        print("contenedor creado:", r)
        for _ in range(30):
            e = P.api(cfg, r["id"], fields="status_code,status")
            print(e, flush=True)
            if e.get("status_code") in ("FINISHED", "ERROR", "EXPIRED"):
                break
            time.sleep(10)
    except Exception as e:
        print("ERROR de la API:", str(e)[:800])


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--probar":
        resto = [a for a in sys.argv[3:] if a and not a.startswith("--")]
        probar(sys.argv[2], resto[0] if resto else None, "STORIES" if "--historia" in sys.argv else "REELS")
    else:
        main()
