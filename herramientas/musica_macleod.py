#!/usr/bin/env python3
"""Descarga la música de Kevin MacLeod (incompetech.com, CC BY 4.0) a musica/ y la registra en musica/pistas.json con su
atribución (se añade sola al texto del post). DIRECTIVA DE VÍDEO 14/11/2026. Uso: python3 herramientas/musica_macleod.py"""
import json, os, subprocess, sys, urllib.parse

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(BASE, "musica")
PISTAS = ["Sneaky Snitch", "Fluffing a Duck", "Monkeys Spinning Monkeys", "Investigations", "Life of Riley"]
URL = "https://incompetech.com/music/royalty-free/mp3-royaltyfree/%s.mp3"


def main():
    fichas = json.load(open(os.path.join(DIR, "pistas.json"), encoding="utf-8")) if os.path.exists(os.path.join(DIR, "pistas.json")) else []
    ya = {f.get("archivo") for f in fichas}
    for t in PISTAS:
        arch = t.lower().replace(" ", "_") + ".mp3"
        ruta = os.path.join(DIR, arch)
        if not os.path.exists(ruta):
            r = subprocess.run(["curl", "-fsSL", "--retry", "3", "-A", "Mozilla/5.0", "-o", ruta, URL % urllib.parse.quote(t)], capture_output=True, text=True)
            if r.returncode != 0 or os.path.getsize(ruta) < 100000:
                print(f"No se pudo descargar «{t}»: {r.stderr[-120:]}"); 
                if os.path.exists(ruta): os.remove(ruta)
                continue
        if arch not in ya:
            fichas.append({"archivo": arch, "titulo": t, "autor": "Kevin MacLeod", "licencia": "CC BY 4.0",
                           "url": "https://incompetech.com/music/royalty-free/", 
                           "atribucion": f"Música: \"{t}\" de Kevin MacLeod (incompetech.com), licencia CC BY 4.0"})
    json.dump(fichas, open(os.path.join(DIR, "pistas.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len([f for f in fichas if os.path.exists(os.path.join(DIR, f['archivo']))])} pistas listas")


if __name__ == "__main__":
    main()
