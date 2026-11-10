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


if __name__ == "__main__":
    main()
