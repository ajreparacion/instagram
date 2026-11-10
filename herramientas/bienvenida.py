#!/usr/bin/env python3
"""Configura las «ice breakers» (preguntas frecuentes del chat) de Instagram vía API de Graph.
Usa el secreto PAGE_TOKEN del entorno (nunca se imprime ni se guarda). Máximo 4 preguntas."""
import json, os, sys, urllib.parse, urllib.request, urllib.error

TOKEN = os.environ.get("PAGE_TOKEN", "")
if not TOKEN:
    sys.exit("Falta el secreto PAGE_TOKEN en el repositorio.")
try:
    _CFG = json.load(open("equipo/config_publico.json", encoding="utf-8"))
except (OSError, ValueError):
    _CFG = {}
VERSION = _CFG.get("version") or "v21.0"
# messenger_profile y me/messages exigen token de PÁGINA; si PAGE_TOKEN es de usuario, se convierte.
from token_pagina import token_de_pagina
TOKEN = token_de_pagina(TOKEN, VERSION, _CFG.get("page_id"))
URL = f"https://graph.facebook.com/{VERSION}/me/messenger_profile"

PREGUNTAS = [
    # Neogest Lab (10/11/2026). Las respuestas están en herramientas/respuestas_chat.py (BOTONES).
    {"question": "¿Qué apps tenéis?", "payload": "APPS"},
    {"question": "Quiero probar una app gratis", "payload": "PRUEBA"},
    {"question": "Quiero una app a medida", "payload": "MEDIDA"},
    {"question": "¿Cuánto cuesta?", "payload": "PRECIO"},
]


def llamar(url, datos=None):
    req = urllib.request.Request(url, data=json.dumps(datos).encode() if datos is not None else None,
                                 method="POST" if datos is not None else "GET",
                                 headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        txt = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(txt)
        except ValueError:
            return e.code, {"raw": txt[:300]}


st, resp = llamar(f"{URL}?platform=instagram", {"platform": "instagram", "ice_breakers": [
    {"call_to_actions": PREGUNTAS[:4], "locale": "default"}]})
print("POST", st, json.dumps(resp, ensure_ascii=False)[:600])
if st != 200:
    err = resp.get("error", {})
    print(f"FALLO: código {err.get('code')} subcódigo {err.get('error_subcode')}: {err.get('message')}")
    sys.exit(1)

st, resp = llamar(f"{URL}?fields=ice_breakers&platform=instagram")
print("GET", st, json.dumps(resp, ensure_ascii=False)[:1200])
# Meta puede devolver las preguntas en lista simple o dentro de "call_to_actions"
ok = False
if st == 200 and resp.get("data"):
    ib = resp["data"][0].get("ice_breakers", [])
    n = sum(len(x["call_to_actions"]) if "call_to_actions" in x else 1 for x in ib)
    ok = n == len(PREGUNTAS[:4])
print("VERIFICADO" if ok else "NO VERIFICADO")
sys.exit(0 if ok else 1)
