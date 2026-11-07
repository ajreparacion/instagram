#!/usr/bin/env python3
"""Responde automáticamente cuando alguien pulsa una de las 4 preguntas de bienvenida (ice breakers)
del chat de Instagram. Revisa las conversaciones recientes con el secreto PAGE_TOKEN y contesta solo
si el último mensaje del chat es una de esas preguntas y aún no se ha respondido. Nunca imprime el token."""
import json, os, sys, time, unicodedata, urllib.parse, urllib.request, urllib.error
from datetime import datetime, timezone

TOKEN = os.environ.get("PAGE_TOKEN", "")
if not TOKEN:
    sys.exit("Falta el secreto PAGE_TOKEN en el repositorio.")
try:
    VERSION = json.load(open("equipo/config_publico.json", encoding="utf-8")).get("version") or "v21.0"
except (OSError, ValueError):
    VERSION = "v21.0"
BASE = f"https://graph.facebook.com/{VERSION}"
GUIA = os.environ.get("GUIA_URL") or "https://ajreparacion.github.io/instagram/guia/"
VENTANA_H = 23  # Instagram solo permite responder dentro de las 24 h siguientes al mensaje

RESPUESTAS = {
    "¿Qué vas a enseñarme?":
        "¡Hola! 👋 Aquí comparto trucos fáciles para usar la inteligencia artificial en tu día a día: "
        "prompts listos para copiar, herramientas gratis y cosas que te ahorran tiempo. Sin tecnicismos.\n\n"
        "Si quieres empezar ya, pídeme la guía de prompts gratis 😉",
    "Quiero la guía de prompts gratis":
        f"¡Aquí la tienes! 📘\n{GUIA}\n\n"
        "Tiene la fórmula para escribir buenos prompts, dónde usar la IA sin pagar y 10 prompts listos para copiar.",
    "¿Cómo uso Claude o ChatGPT gratis?":
        "Puedes usar las dos gratis, solo con una cuenta: Claude en claude.ai y ChatGPT en chatgpt.com "
        "(las dos tienen app). La versión gratis tiene un límite de mensajes: si llegas al límite en una, "
        "sigue en la otra o en Gemini (gemini.google.com).\n\n"
        f"En la guía te lo explico con prompts para copiar: {GUIA}",
    "Quiero proponerte un tema":
        "¡Me encanta! ✍️ Escríbeme en un mensaje el tema o la duda que quieres que explique "
        "y lo apunto para un próximo vídeo.",
}


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return "".join(c for c in t if c.isalnum() or c == " ").split()


CLAVES = {" ".join(norm(k)): v for k, v in RESPUESTAS.items()}


def llamar(ruta, datos=None, params=None):
    url = f"{BASE}/{ruta}" + ("?" + urllib.parse.urlencode(params) if params else "")
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


def fallo(paso, resp):
    err = resp.get("error", {})
    sys.exit(f"FALLO en {paso}: código {err.get('code')} subcódigo {err.get('error_subcode')}: {err.get('message')}")


st, yo = llamar("me", params={"fields": "id,instagram_business_account{id,username}"})
if st != 200:
    fallo("leer la página", yo)
ig = yo.get("instagram_business_account") or {}
MIS_IDS = {x for x in (ig.get("id"), yo.get("id")) if x}
MI_USUARIO = (ig.get("username") or "").lower()

st, conv = llamar("me/conversations", params={
    "platform": "instagram", "limit": 25,
    "fields": "updated_time,messages.limit(3){message,from,created_time}"})
if st != 200:
    fallo("leer conversaciones", conv)

ahora = datetime.now(timezone.utc)
enviadas = revisadas = 0
for c in conv.get("data", []):
    msgs = (c.get("messages") or {}).get("data", [])
    if not msgs:
        continue
    revisadas += 1
    ultimo = msgs[0]  # la API devuelve primero el más reciente
    de = ultimo.get("from") or {}
    if de.get("id") in MIS_IDS or (de.get("username") or "").lower() == MI_USUARIO:
        continue  # el último mensaje ya es nuestro: nada que contestar
    texto = CLAVES.get(" ".join(norm(ultimo.get("message"))))
    if not texto:
        continue
    try:
        hora = datetime.strptime(ultimo["created_time"], "%Y-%m-%dT%H:%M:%S%z")
    except (KeyError, ValueError):
        continue
    if (ahora - hora).total_seconds() > VENTANA_H * 3600:
        continue
    st, r = llamar("me/messages", {"recipient": {"id": de["id"]}, "message": {"text": texto}})
    if st == 200:
        enviadas += 1
        print(f"Respondido a @{de.get('username', '?')}: «{ultimo.get('message')}»")
    else:
        err = r.get("error", {})
        print(f"No se pudo responder a @{de.get('username', '?')}: código {err.get('code')}: {err.get('message')}")
    time.sleep(1)

print(f"Conversaciones revisadas: {revisadas}. Respuestas enviadas: {enviadas}.")
