#!/usr/bin/env python3
"""Redes vía Metricool (plan gratis) — SEGUNDA VÍA independiente de Buffer para no depender de
una sola herramienta ni de la aprobación de la API propia de TikTok for Developers (orden del
dueño, 20/11/2026: "busca opciones con planes gratis y combinamos para no depender solo de 1").

Uso: python3 herramientas/redes_metricool.py <canal> [--simular]      canal = tiktok (de momento)

Reutiliza TAL CUAL la selección de piezas, el texto por canal y la subida a la release pública
«redes» de herramientas/redes_buffer.py (misma fuente de verdad, canal nuevo: equipo/metricool/).
Solo cambia la llamada a la API: Metricool en vez de Buffer.

Secretos: METRICOOL_TOKEN, METRICOOL_USER_ID, METRICOOL_BLOG_ID (los tres obligatorios; se
obtienen una sola vez en Configuración de la cuenta > API de Metricool, los conecta el dueño).
Sin ellos, o sin canal conectado, no hace nada y termina bien.

AVISO DE VERIFICACIÓN PENDIENTE (cero alucinaciones, orden fija del proyecto): la documentación
pública de Metricool confirma el endpoint, la autenticación (header X-Mc-Auth + userId/blogId),
y los campos generales del post (publicationDate, text, providers). NO documenta en público los
campos exactos de "tiktokData" (privacidad, aviso de contenido generado por IA, dúo/comentarios)
ni un endpoint de normalizado de VÍDEO (solo está documentado el de imagen). Por eso, hasta que
alguien abra una vez https://app.metricool.com/api/swagger.json en un navegador (bloqueado aquí
por robots.txt) y confirme esos campos, este script:
  1. Publica con draft=true (SIEMPRE queda en Metricool como borrador, nunca auto-publicado),
     para que el dueño revise y complete a mano los campos propios de TikTok la primera vez.
  2. No manda "tiktokData": si el campo es obligatorio, Metricool devolverá el error exacto con
     el nombre del campo que falta, y eso sí es una fuente fiable para corregir el script.
Cuando el dueño confirme los campos (o tras ver el primer error real de la API), se quita el
draft=true y se completa tiktokData — lo hace quien lea este aviso, no se da por supuesto antes.
"""
import glob
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from redes_buffer import RAIZ, MADRID, candidatos, huecos_libres, leer, escribir, texto_canal, medio_publico  # noqa: E402

METRICOOL = "https://app.metricool.com/api"


def _pedir(metodo, ruta, token, user_id, blog_id, cuerpo=None):
    qs = urllib.parse.urlencode({"userId": user_id, "blogId": blog_id})
    sep = "&" if "?" in ruta else "?"
    req = urllib.request.Request(
        METRICOOL + ruta + sep + qs,
        data=json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None,
        method=metodo,
        headers={"X-Mc-Auth": token, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"Metricool {metodo} {ruta}: HTTP {e.code} — {detalle}")


def normalizar_media(url, token, user_id, blog_id, es_imagen):
    """Solo hay endpoint público confirmado para imagen. Para vídeo se prueba el mismo patrón
    (normalize/video/url); si Metricool lo rechaza, el error queda anotado tal cual en
    ultimo_error para corregirlo con el mensaje real, nunca adivinado de antemano."""
    tipo = "image" if es_imagen else "video"
    datos = _pedir("GET", f"/actions/normalize/{tipo}/url?url={urllib.parse.quote(url, safe='')}",
                    token, user_id, blog_id)
    media_id = datos.get("id") or datos.get("mediaId")
    if not media_id:
        raise RuntimeError(f"Metricool no devolvió mediaId al normalizar: {json.dumps(datos)[:300]}")
    return media_id


def crear_post(token, user_id, blog_id, texto, cuando_iso, media_id, canal):
    cuando = datetime.fromisoformat(cuando_iso.replace("Z", "+00:00")).astimezone(MADRID)
    cuerpo = {
        "text": texto,
        "publicationDate": {"dateTime": cuando.strftime("%Y-%m-%dT%H:%M:%S"), "timezone": "Europe/Madrid"},
        "providers": [{"network": canal}],
        "draft": True,  # ver AVISO DE VERIFICACIÓN PENDIENTE arriba: no se quita sin confirmar tiktokData
        "media": {"mediaId": media_id} if media_id else None,
    }
    if cuerpo["media"] is None:
        del cuerpo["media"]
    r = _pedir("POST", "/v2/scheduler/posts", token, user_id, blog_id, cuerpo)
    pid = r.get("id") or (r.get("data") or {}).get("id")
    if not pid:
        raise RuntimeError(f"Metricool no confirmó el id del post creado: {json.dumps(r)[:300]}")
    return pid


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    canal = args[0] if args else ""
    if canal not in ("tiktok",):
        raise SystemExit("Uso: redes_metricool.py tiktok [--simular]  (de momento solo tiktok)")
    simular = "--simular" in sys.argv
    carpeta = os.path.join(RAIZ, "equipo", "metricool")
    cfg = leer(os.path.join(carpeta, "config.json"), {})
    ruta_estado = os.path.join(carpeta, "estado.json")
    estado = leer(ruta_estado, {"enviados": {}, "ultimo_error": ""})
    ahora = datetime.now(timezone.utc)
    ahora_iso = ahora.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    pendientes = sum(1 for v in estado["enviados"].values() if v.get("dueAt", "") > ahora_iso)
    cupo = max(0, cfg.get("max_pendientes", 8) - pendientes)
    # MISMA cuenta de TikTok que Buffer (equipo/tiktok): nunca repetir lo que Buffer ya mandó ahí,
    # para que las "2 vías" sean respaldo/variedad, no el mismo vídeo publicado dos veces.
    estado_buffer = leer(os.path.join(RAIZ, "equipo", canal, "estado.json"), {"enviados": {}})
    estado_para_elegir = {"enviados": {**estado_buffer.get("enviados", {}), **estado["enviados"]}}
    lista = candidatos(cfg, estado_para_elegir)
    print(f"metricool/{canal}: {pendientes} programados, cupo {cupo}, {len(lista)} piezas disponibles")
    if simular:
        for (nombre, post, _), cuando in zip(lista, huecos_libres(cfg, estado, ahora)):
            print(f"\n=== {nombre} · {cuando}\n{texto_canal(nombre, post, cfg, canal)}")
        return
    token = os.environ.get("METRICOOL_TOKEN")
    user_id = os.environ.get("METRICOOL_USER_ID")
    blog_id = os.environ.get("METRICOOL_BLOG_ID")
    if not (token and user_id and blog_id):
        print("metricool en espera: faltan METRICOOL_TOKEN / METRICOOL_USER_ID / METRICOOL_BLOG_ID (ver equipo/metricool/LEEME.md).")
        return
    antes = json.dumps(estado, sort_keys=True)
    try:
        for (nombre, post, res), cuando in zip(lista[:cupo], huecos_libres(cfg, estado, ahora)):
            url = medio_publico(nombre, res["media_id"], canal, cfg)
            media_id = normalizar_media(url, token, user_id, blog_id, es_imagen=cfg.get("medio") == "imagen")
            pid = crear_post(token, user_id, blog_id, texto_canal(nombre, post, cfg, canal), cuando, media_id, canal)
            estado["enviados"][nombre] = {"dueAt": cuando, "metricool_id": pid, "enviado": ahora_iso,
                                          "fichero": os.path.basename(url), "borrador": True}
            estado["ultimo_error"] = ""
            escribir(ruta_estado, estado)
            print(f"{nombre}: BORRADOR creado en Metricool/{canal} para {cuando} (revisar y publicar a mano hasta confirmar tiktokData)")
    except Exception as e:
        estado["ultimo_error"] = f"{ahora_iso} · {e}"[:500]
        print(f"ERROR metricool/{canal}:", estado["ultimo_error"])
    if json.dumps(estado, sort_keys=True) != antes:
        escribir(ruta_estado, estado)


if __name__ == "__main__":
    main()
