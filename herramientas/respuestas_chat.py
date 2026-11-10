#!/usr/bin/env python3
"""Contestador gratuito del chat de Instagram de Neogest Lab (Graph API + PAGE_TOKEN, sin coste).

Contesta dos cosas, solo dentro de la ventana de 24 h que permite Instagram:
1. Las 4 preguntas de bienvenida (ice breakers) que configura herramientas/bienvenida.py.
2. Mensajes libres cortos con palabras clave (precio, a medida, prueba, apps, hola...).

Reglas para no molestar:
- Solo responde si el último mensaje del chat es de la otra persona.
- Si el dueño ya ha escrito a mano en ese chat (un mensaje que no es del contestador),
  el contestador se calla en los mensajes libres: esa conversación la lleva el dueño.
- Nunca repite la misma respuesta en un chat, y no contesta mensajes largos (> 20 palabras):
  esos los lee y contesta el dueño.
- Nunca da precios ni promete plazos.
Con DRY_RUN=1 no envía nada: solo imprime qué contestaría. Nunca imprime el token."""
import json, os, sys, time, unicodedata, urllib.parse, urllib.request, urllib.error
from datetime import datetime, timezone

TOKEN = os.environ.get("PAGE_TOKEN", "")
if not TOKEN:
    sys.exit("Falta el secreto PAGE_TOKEN en el repositorio.")
DRY = os.environ.get("DRY_RUN", "") not in ("", "0", "false")
try:
    _CFG = json.load(open("equipo/config_publico.json", encoding="utf-8"))
except (OSError, ValueError):
    _CFG = {}
VERSION = _CFG.get("version") or "v21.0"
# messenger_profile y me/messages exigen token de PÁGINA; si PAGE_TOKEN es de usuario, se convierte.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from token_pagina import token_de_pagina
TOKEN = token_de_pagina(TOKEN, VERSION, _CFG.get("page_id"))
BASE = f"https://graph.facebook.com/{VERSION}"
VENTANA_H = 23  # Instagram solo permite responder dentro de las 24 h siguientes al mensaje
MAX_PALABRAS = 20

CENTRO = "https://centro-de-contenido-apps-2f0a3cd6.base44.app/?src=instagram"
PRUEBA_7D = "https://centro-de-contenido-apps-2f0a3cd6.base44.app/solicitar?app=gestion-integral-7d&src=instagram"
CIERRE = "sin tarjeta, sin datos bancarios y sin compromiso"

TEXTOS = {
    "APPS":
        "¡Hola! 👋 Somos Neogest Lab: creamos apps para negocios y para el día a día. Algunas:\n"
        "• Gestión Integral 7D: presupuestos, pedidos, albaranes y facturas para autónomos y pymes.\n"
        "• AJ Sistema: web con solicitudes y gestión interna para cualquier negocio.\n"
        "• Studio Beats PRO: crea un beat, graba tu voz y exporta tu canción.\n\n"
        f"Las tienes todas aquí: {CENTRO}\n\n"
        "¿Para qué la necesitas? Cuéntamelo y te digo cuál te encaja.",
    "PRUEBA":
        f"¡Genial! 🙌 Pide tu prueba gratuita: {CIERRE}.\n"
        f"Elige la app y rellena la solicitud aquí: {CENTRO}\n\n"
        f"Si tienes un negocio, empieza por Gestión Integral 7D: {PRUEBA_7D}",
    "MEDIDA":
        "¡Nos encanta! 💡 Hacemos apps a medida para cualquier negocio o persona. Cuéntame en un mensaje:\n"
        "1) A qué te dedicas.\n"
        "2) Qué quieres que haga la app.\n"
        "3) Qué usas ahora (papel, Excel, otra app...).\n\n"
        "Te contesto personalmente lo antes posible.",
    "PRECIO":
        "Depende de la app y de lo que necesites, así que no damos un precio cerrado por aquí. "
        f"Lo que sí puedes hacer ya es pedir tu prueba gratuita, {CIERRE}: {CENTRO}\n\n"
        "Si buscas una app a medida, cuéntame qué necesitas y te contesto personalmente con lo que costaría.",
    "SALUDO":
        "¡Hola! 👋 Gracias por escribir a Neogest Lab. Dime qué buscas:\n"
        "• Escribe APPS para ver nuestras apps.\n"
        "• PRUEBA para probar una gratis.\n"
        "• MEDIDA si quieres una app a medida.\n"
        "• PRECIO si quieres saber cuánto cuesta.\n\n"
        "O cuéntame tu idea directamente y te contesto personalmente.",
}

# Preguntas de bienvenida (deben coincidir con herramientas/bienvenida.py). Las antiguas siguen
# mapeadas por si alguien tiene el chat abierto con las preguntas viejas.
BOTONES = {
    "¿Qué apps tenéis?": "APPS",
    "Quiero probar una app gratis": "PRUEBA",
    "Quiero una app a medida": "MEDIDA",
    "¿Cuánto cuesta?": "PRECIO",
    "¿Qué vas a enseñarme?": "SALUDO",
    "Quiero la guía de prompts gratis": "SALUDO",
    "¿Cómo uso Claude o ChatGPT gratis?": "SALUDO",
    "Quiero proponerte un tema": "SALUDO",
}

# Palabras clave de mensajes libres, por prioridad (la primera que encaje gana).
CLAVES = [
    ("MEDIDA", ["medida", "personalizada", "personalizado", "me haces", "hacerme", "crearme", "mi idea",
                "una idea", "tengo una idea", "desarrollar", "desarrollo", "quiero una app", "necesito una app",
                "quiero una aplicacion", "necesito una aplicacion", "programar"]),
    ("PRECIO", ["precio", "precios", "cuesta", "cuestan", "cuanto vale", "cuanto valen", "tarifa", "tarifas",
                "coste", "costo", "presupuesto", "cuanto es", "cuanto cobras", "cuanto cobrais", "pagar"]),
    ("PRUEBA", ["prueba", "probar", "demo", "gratis", "gratuita", "gratuito"]),
    ("APPS", ["apps", "app", "aplicacion", "aplicaciones", "catalogo"]),
    ("SALUDO", ["hola", "buenas", "info", "informacion", "buenos dias", "buenas tardes", "buenas noches", "hey"]),
]


def norm(t):
    t = unicodedata.normalize("NFKD", t or "").encode("ascii", "ignore").decode().lower()
    return " ".join("".join(c if c.isalnum() else " " for c in t).split())


BOTONES_N = {norm(k): v for k, v in BOTONES.items()}
TEXTOS_N = {norm(v): k for k, v in TEXTOS.items()}


def regla_libre(texto):
    """Devuelve la clave de respuesta para un mensaje libre, o None si no toca contestar."""
    n = norm(texto)
    if not n or len(n.split()) > MAX_PALABRAS:
        return None
    rodeado = f" {n} "
    for clave, palabras in CLAVES:
        if any(f" {p} " in rodeado for p in palabras):
            return clave
    return None


def elegir(msgs, es_mio):
    """msgs: más reciente primero. Devuelve (clave, motivo) o (None, motivo)."""
    ultimo = msgs[0]
    if es_mio(ultimo):
        return None, "el último mensaje ya es nuestro"
    enviados = {TEXTOS_N.get(norm(m.get("message"))) for m in msgs if es_mio(m)}
    dueno_a_mano = any(es_mio(m) and norm(m.get("message")) not in TEXTOS_N for m in msgs)
    texto = ultimo.get("message") or ""
    clave = BOTONES_N.get(norm(texto))
    if clave:
        motivo = "botón de bienvenida"
    else:
        if dueno_a_mano:
            return None, "el dueño ya lleva esta conversación"
        clave = regla_libre(texto)
        motivo = "palabra clave"
        if not clave:
            return None, "sin palabra clave o mensaje largo: lo contesta el dueño"
    if clave in enviados:
        return None, f"ya se le envió la respuesta {clave}"
    return clave, motivo


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


def main():
    st, yo = llamar("me", params={"fields": "id,instagram_business_account{id,username}"})
    if st != 200:
        fallo("leer la página", yo)
    ig = yo.get("instagram_business_account") or {}
    mis_ids = {x for x in (ig.get("id"), yo.get("id"), _CFG.get("ig_user_id")) if x}
    mi_usuario = (ig.get("username") or "").lower()
    print(f"Cuenta: @{mi_usuario or '?'}" + (" · MODO PRUEBA (no se envía nada)" if DRY else ""))

    def es_mio(m):
        de = m.get("from") or {}
        return de.get("id") in mis_ids or (de.get("username") or "").lower() == mi_usuario

    st, conv = llamar("me/conversations", params={
        "platform": "instagram", "limit": 25,
        "fields": "updated_time,messages.limit(10){message,from,created_time}"})
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
        quien = f"@{de.get('username', '?')}"
        try:
            hora = datetime.strptime(ultimo["created_time"], "%Y-%m-%dT%H:%M:%S%z")
        except (KeyError, ValueError):
            continue
        if (ahora - hora).total_seconds() > VENTANA_H * 3600:
            continue
        clave, motivo = elegir(msgs, es_mio)
        if not clave:
            print(f"{quien}: no se contesta ({motivo}).")
            continue
        if DRY:
            print(f"{quien}: contestaría {clave} ({motivo}) a «{(ultimo.get('message') or '')[:80]}»")
            continue
        st, r = llamar("me/messages", {"recipient": {"id": de["id"]}, "message": {"text": TEXTOS[clave]}})
        if st == 200:
            enviadas += 1
            print(f"{quien}: respondido {clave} ({motivo}).")
        else:
            err = r.get("error", {})
            print(f"{quien}: no se pudo responder: código {err.get('code')}: {err.get('message')}")
        time.sleep(1)

    print(f"Conversaciones revisadas: {revisadas}. Respuestas enviadas: {enviadas}.")


if __name__ == "__main__":
    main()
