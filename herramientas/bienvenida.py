#!/usr/bin/env python3
"""Configura las «ice breakers» (preguntas frecuentes del chat) de Instagram vía API de Graph.
Usa el secreto PAGE_TOKEN del entorno (nunca se imprime ni se guarda). Máximo 4 preguntas."""
import json, os, sys, urllib.parse, urllib.request, urllib.error

TOKEN = os.environ.get("PAGE_TOKEN", "")
if not TOKEN:
    sys.exit("Falta el secreto PAGE_TOKEN en el repositorio.")
try:
    VERSION = json.load(open("equipo/config_publico.json", encoding="utf-8")).get("version") or "v21.0"
except (OSError, ValueError):
    VERSION = "v21.0"
URL = f"https://graph.facebook.com/{VERSION}/me/messenger_profile"

PREGUNTAS = [
    {"question": "¿Qué vas a enseñarme?", "payload": "BIENVENIDA"},
    {"question": "Quiero la guía de prompts gratis", "payload": "GUIA"},
    {"question": "¿Cómo uso Claude o ChatGPT gratis?", "payload": "GRATIS"},
    {"question": "Quiero proponerte un tema", "payload": "TEMA"},
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
ok = st == 200 and any(len(x.get("call_to_actions", [])) == 4 for x in resp.get("data", [{}])[0].get("ice_breakers", [])) \
    if st == 200 and resp.get("data") else False
print("VERIFICADO" if ok else "NO VERIFICADO")
sys.exit(0 if ok else 1)
