#!/usr/bin/env python3
"""Prueba del motor nuevo (edge-tts + música MacLeod + máster) y del control de audio. No publica nada.
Uso: python3 herramientas/prueba_edge.py [guion.json]  -> /tmp/edge/salida/edge_reel.mp4, edge_reel.mp3, control_audio.json"""
import json, os, shutil, subprocess, sys, time
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path[:0] = [AQUI, os.path.dirname(AQUI)]
import publicar_gh as pg          # noqa: E402
import control_audio as ca        # noqa: E402

guion = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(AQUI, "ejemplo_horas_extra_p2.json"))
SAL = "/tmp/edge/salida"; trabajo = "/tmp/edge/render"
shutil.rmtree("/tmp/edge", ignore_errors=True); os.makedirs(SAL); os.makedirs(trabajo)
video = os.path.join(trabajo, "video.mp4"); t0 = time.time()
motor = pg.renderizar_guion(guion, video, trabajo)
shutil.copy(video, f"{SAL}/edge_reel.mp4")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vn", "-c:a", "libmp3lame", "-b:a", "192k", "-ar", "48000", f"{SAL}/edge_reel.mp3"], check=True)
lufs, pico = pg._lufs_pico(video)
res = ca.control(video, guion)
res.update(motor_voz=motor, render_s=round(time.time() - t0), lufs=lufs, pico_dbfs=pico)
json.dump(res, open(f"{SAL}/control_audio.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(res, ensure_ascii=False, indent=1))
