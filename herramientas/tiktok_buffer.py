#!/usr/bin/env python3
"""TikTok @neogestlab · programa en Buffer (plan gratis) los reels ya aprobados y publicados en Instagram.

Qué hace en cada pasada (workflow tiktok.yml, una vez al día):
  1. Elige las siguientes piezas de publicados/ (reel, calidad aprobada, render desde el 14/11/2026, sin cierres
     prohibidos, no enviadas aún), en el orden de equipo/tiktok/config.json y alternando 2 de El Jambo por 1 de app.
  2. Descarga el vídeo de Instagram (media_url de la API), lo sube a la release pública «tiktok» y crea el post en
     Buffer con el texto adaptado a TikTok, en el siguiente hueco libre (config.json: «huecos», hora de Madrid).
  3. Mantiene como mucho «max_pendientes» posts programados (el plan gratis de Buffer admite 10 por canal).
  4. Anota lo enviado en equipo/tiktok/estado.json (lo confirma el workflow).

Secretos (GitHub Actions): BUFFER_API_KEY (obligatorio), PAGE_TOKEN (ya existe), BUFFER_TIKTOK_CHANNEL_ID (opcional).
Sin BUFFER_API_KEY no hace nada y termina bien: TikTok queda en espera hasta que el dueño conecte Buffer.

Uso: python3 herramientas/tiktok_buffer.py            (pasada real)
     python3 herramientas/tiktok_buffer.py --simular  (enseña qué enviaría y con qué texto; no llama a nada)
"""
import glob
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(RAIZ, "equipo", "tiktok")
MADRID = ZoneInfo("Europe/Madrid")
RELEASE = "tiktok"
REPO = os.environ.get("GITHUB_REPOSITORY", "ajreparacion/instagram")
BUFFER = "https://api.buffer.com"
PROHIBIDO = re.compile(r"Escr[ií]beme|[Cc]omenta [A-ZÁÉÍÓÚ]{3,}\b|te (lo )?env[ií]o|palabra clave", re.U)
CIERRE = "Pide tu prueba gratuita: sin tarjeta, sin datos bancarios y sin compromiso. Enlace en el perfil."


def leer(ruta, defecto):
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return defecto


def escribir(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
        f.write("\n")


def es_jambo(nombre, post):
    return "jambo" in nombre or "jambo" in str(post.get("formato", "")).lower()


def texto_tiktok(nombre, post, cfg):
    """Mismo texto ya verificado del post de Instagram, con el cierre único y etiquetas de TikTok."""
    lineas, tiene_ia = [], False
    for linea in str(post.get("texto", "")).split("\n"):
        l = linea.strip()
        if not l or re.fullmatch(r"(#\w+\s*)+", l, re.U):
            continue                                   # fuera las etiquetas de Instagram
        if l.lower().startswith("pide tu prueba gratuita") or l.lower().startswith("pruébala gratis"):
            continue                                   # el cierre se pone una sola vez, abajo
        l = re.sub(r"\s*(→\s*)?enlace /solicitar del perfil.*$", "", l, flags=re.I)
        if "generad" in l.lower() and "ia" in l.lower():
            tiene_ia = True
        lineas.append(l)
    cierre = cfg.get("cierres", {}).get(post.get("app_slug", ""), CIERRE)
    etiquetas = cfg["etiquetas"]["jambo" if es_jambo(nombre, post) else "app"]
    if post.get("app_slug"):
        etiquetas = etiquetas + " #" + re.sub(r"[^a-z0-9]", "", post["app_slug"].lower())
    cuerpo = lineas + [cierre]
    if not tiene_ia:
        cuerpo.append("Voz generada por IA")
    return "\n".join(cuerpo + [etiquetas])[:2100]


def candidatos(cfg, estado):
    hechos, desde = set(estado.get("enviados", {})), cfg["render_desde"]
    excluir, piezas = set(cfg.get("excluir", [])), {}
    for carpeta in sorted(glob.glob(os.path.join(RAIZ, "publicados", "*", ""))):
        nombre = os.path.basename(carpeta.rstrip("/"))
        post = leer(carpeta + "post.json", {})
        cal = leer(carpeta + "calidad.json", {})
        res = leer(carpeta + "resultado.json", {})
        if nombre in hechos or nombre in excluir or post.get("tipo") != "reel":
            continue
        if not cal.get("aprobado") or not res.get("media_id"):
            continue
        if str(post.get("renderizado") or "")[:10] < desde and nombre not in cfg.get("incluir_antiguos", []):
            continue                                   # anteriores al logo 2026: solo si Calidad los incluye a mano
        if PROHIBIDO.search(str(post.get("texto", ""))):
            continue
        if re.search(r"parte\s*2|_parte2", nombre + " " + str(post.get("texto", ""))[:40], re.I) \
                and nombre not in cfg.get("incluir_antiguos", []):
            continue                                   # una «Parte 2» sin su parte 1 en TikTok no se entiende
        piezas[nombre] = (post, res)
    orden = [n for n in cfg.get("orden_inicial", []) if n in piezas] + \
            [n for n in sorted(piezas) if n not in cfg.get("orden_inicial", [])]
    jambo = [n for n in orden if es_jambo(n, piezas[n][0])]
    apps = [n for n in orden if not es_jambo(n, piezas[n][0])]
    mezcla = []
    while jambo or apps:                               # 2 de El Jambo por 1 de app
        mezcla += jambo[:2]; jambo = jambo[2:]
        mezcla += apps[:1]; apps = apps[1:]
    return [(n, *piezas[n]) for n in mezcla]


def huecos_libres(cfg, estado, ahora):
    ocupados = {v.get("dueAt") for v in estado.get("enviados", {}).values()}
    dia = ahora.astimezone(MADRID).date()
    for _ in range(30):
        for hhmm in cfg["huecos"]:
            h, m = map(int, hhmm.split(":"))
            t = datetime(dia.year, dia.month, dia.day, h, m, tzinfo=MADRID).astimezone(timezone.utc)
            iso = t.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            if t > ahora + timedelta(minutes=45) and iso not in ocupados:
                yield iso
        dia += timedelta(days=1)


def buffer(consulta):
    req = urllib.request.Request(BUFFER, data=json.dumps({"query": consulta}).encode(), method="POST", headers={
        "Content-Type": "application/json", "Authorization": "Bearer " + os.environ["BUFFER_API_KEY"]})
    with urllib.request.urlopen(req, timeout=120) as r:
        datos = json.load(r)
    if datos.get("errors"):
        raise RuntimeError("Buffer: " + json.dumps(datos["errors"], ensure_ascii=False)[:400])
    return datos["data"]


def canal_tiktok():
    fijo = os.environ.get("BUFFER_TIKTOK_CHANNEL_ID", "").strip()
    if fijo:
        return fijo
    for org in buffer("query { account { organizations { id name } } }")["account"]["organizations"]:
        canales = buffer('query { channels(input: {organizationId: %s}) { id name service } }' % json.dumps(org["id"]))
        for c in canales["channels"]:
            if str(c.get("service", "")).lower() == "tiktok":
                return c["id"]
    raise RuntimeError("Buffer no tiene ningún canal de TikTok conectado")


def gh(*args, check=True):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError("gh " + " ".join(args[:3]) + ": " + r.stderr.strip()[-300:])
    return r


def video_publico(nombre, media_id):
    """Instagram -> release «tiktok» (URL pública y estable para que Buffer la descargue)."""
    cfg = leer(os.path.join(RAIZ, "equipo", "config_publico.json"), {})
    url = "https://graph.facebook.com/%s/%s?%s" % (cfg.get("version", "v27.0"), media_id, urllib.parse.urlencode(
        {"fields": "media_url", "access_token": os.environ["PAGE_TOKEN"]}))
    with urllib.request.urlopen(url, timeout=60) as r:
        media = json.load(r).get("media_url")
    if not media:
        raise RuntimeError("Instagram no da media_url")
    fichero = "/tmp/%s.mp4" % nombre
    urllib.request.urlretrieve(media, fichero)
    if os.path.getsize(fichero) < 200_000:
        raise RuntimeError("vídeo descargado demasiado pequeño")
    if gh("release", "view", RELEASE, check=False).returncode != 0:
        gh("release", "create", RELEASE, "--title", "Vídeos para TikTok", "--notes", "Copias temporales para Buffer.")
    gh("release", "upload", RELEASE, fichero, "--clobber")
    return "https://github.com/%s/releases/download/%s/%s.mp4" % (REPO, RELEASE, nombre)


def crear_post(canal, texto, url, cuando):
    q = """mutation { createPost(input: {text: %s, channelId: %s, schedulingType: automatic, mode: customScheduled,
      dueAt: %s, assets: [{video: {url: %s, metadata: {thumbnailOffset: 0}}}]}) {
      ... on PostActionSuccess { post { id } } ... on MutationError { message } } }""" % (
        json.dumps(texto, ensure_ascii=False), json.dumps(canal), json.dumps(cuando), json.dumps(url))
    r = buffer(q)["createPost"]
    if not r.get("post"):
        raise RuntimeError("Buffer rechazó el post: " + str(r.get("message")))
    return r["post"]["id"]


def limpiar_release(estado, ahora):
    limite = (ahora - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    for nombre, v in estado.get("enviados", {}).items():
        if v.get("dueAt", "9") < limite and not v.get("limpio"):
            gh("release", "delete-asset", RELEASE, nombre + ".mp4", "-y", check=False)
            v["limpio"] = True


def main():
    simular = "--simular" in sys.argv
    cfg = leer(os.path.join(DIR, "config.json"), {})
    ruta_estado = os.path.join(DIR, "estado.json")
    estado = leer(ruta_estado, {"enviados": {}, "ultimo_error": ""})
    ahora = datetime.now(timezone.utc)
    ahora_iso = ahora.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    pendientes = sum(1 for v in estado["enviados"].values() if v.get("dueAt", "") > ahora_iso)
    cupo = max(0, cfg["max_pendientes"] - pendientes)
    lista = candidatos(cfg, estado)
    print(f"TikTok: {pendientes} programados, cupo {cupo}, {len(lista)} piezas disponibles")
    if simular:
        for (nombre, post, _), cuando in zip(lista, huecos_libres(cfg, estado, ahora)):
            print(f"\n=== {nombre} · {cuando}\n{texto_tiktok(nombre, post, cfg)}")
        return
    if not os.environ.get("BUFFER_API_KEY"):
        print("TikTok en espera: falta el secreto BUFFER_API_KEY (ver equipo/tiktok/LEEME.md).")
        return
    if not cupo or not lista:
        limpiar_release(estado, ahora); escribir(ruta_estado, estado)
        return
    try:
        canal = canal_tiktok()
        for (nombre, post, res), cuando in zip(lista[:cupo], huecos_libres(cfg, estado, ahora)):
            url = video_publico(nombre, res["media_id"])
            pid = crear_post(canal, texto_tiktok(nombre, post, cfg), url, cuando)
            estado["enviados"][nombre] = {"dueAt": cuando, "buffer_id": pid, "enviado": ahora_iso}
            estado["ultimo_error"] = ""
            escribir(ruta_estado, estado)
            print(f"{nombre}: programado en TikTok para {cuando}")
    except Exception as e:                             # no tumba el workflow: queda anotado para el Supervisor
        estado["ultimo_error"] = f"{ahora_iso} · {e}"[:500]
        print("ERROR TikTok:", estado["ultimo_error"])
    limpiar_release(estado, ahora)
    escribir(ruta_estado, estado)


if __name__ == "__main__":
    main()
