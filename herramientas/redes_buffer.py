#!/usr/bin/env python3
"""Redes vía Buffer (plan gratis): TikTok, LinkedIn y Google Business Profile de Neogest Lab.

Uso: python3 herramientas/redes_buffer.py <canal> [--simular]      canal = tiktok | linkedin | google

En cada pasada (workflow redes_buffer.yml) y para ese canal:
  1. Elige las siguientes piezas de publicados/ (reel, calidad aprobada, render desde «render_desde», sin cierres
     prohibidos, sin «Parte 2», no enviadas aún), según equipo/<canal>/config.json (orden, mezcla Jambo/app, solo_apps).
  2. Descarga el vídeo de Instagram (media_url). Si el canal publica vídeo lo sube tal cual a la release pública
     «redes»; si publica imagen (Google no admite vídeo) saca el primer fotograma en 1080x1080 con ffmpeg.
  3. Crea el post en Buffer con el texto adaptado al canal, en el siguiente hueco libre (hora de Madrid).
  4. Mantiene como mucho «max_pendientes» posts programados (Buffer gratis admite 10 por canal) y anota lo enviado
     en equipo/<canal>/estado.json (lo confirma el workflow).

Secretos: BUFFER_API_KEY (obligatorio), PAGE_TOKEN (ya existe). Sin BUFFER_API_KEY, o si Buffer aún no tiene ese
canal conectado, no hace nada y termina bien: el canal queda en espera. --simular enseña qué enviaría, sin llamar a nada.
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
MADRID = ZoneInfo("Europe/Madrid")
RELEASE = "redes"
REPO = os.environ.get("GITHUB_REPOSITORY", "ajreparacion/instagram")
BUFFER = "https://api.buffer.com"
PROHIBIDO = re.compile(r"Escr[ií]beme|[Cc]omenta [A-ZÁÉÍÓÚ]{3,}\b|te (lo )?env[ií]o|palabra clave", re.U)
CIERRE = "Pide tu prueba gratuita: sin tarjeta, sin datos bancarios y sin compromiso"
SOLICITAR = "https://centro-de-contenido-apps-2f0a3cd6.base44.app/solicitar"


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


def enlace(post, canal):
    q = {"app": post["app_slug"]} if post.get("app_slug") else {}
    q["src"] = canal
    return SOLICITAR + "?" + urllib.parse.urlencode(q)


def texto_canal(nombre, post, cfg, canal):
    """Mismo texto ya verificado del post de Instagram, con el cierre único y lo propio de cada canal."""
    lineas, tiene_ia = [], False
    for linea in str(post.get("texto", "")).split("\n"):
        l = linea.strip()
        if not l or re.fullmatch(r"(#\w+\s*)+", l, re.U):
            continue                                   # fuera las etiquetas de Instagram
        if l.lower().startswith("pide tu prueba gratuita") or l.lower().startswith("pruébala gratis"):
            continue                                   # el cierre se pone una sola vez, abajo
        if canal == "google" and re.search(r"m[aá]ndaselo|cu[eé]ntalo en comentarios\.?$", l, re.I):
            continue                                   # en la ficha de Google no hay comentarios ni reenvíos
        l = re.sub(r"\s*(→\s*)?enlace /solicitar del perfil.*$", "", l, flags=re.I)
        l = re.sub(r"\s*Enlace en el perfil\.?$", "", l, flags=re.I)
        if "generad" in l.lower() and "ia" in l.lower():
            tiene_ia = True
            if canal == "google":
                continue                               # en Google va una imagen fija, sin voz
        if l:
            lineas.append(l)
    cierre = cfg.get("cierres", {}).get(post.get("app_slug", ""), CIERRE)
    if cfg.get("enlace_en_texto"):
        cierre += ": " + enlace(post, canal)
    elif canal == "google":
        cierre += ". Pulsa el botón."
    else:
        cierre += ". Enlace en el perfil."
    cuerpo = lineas + [cierre]
    if not tiene_ia and cfg["medio"] == "video":
        cuerpo.append("Voz generada por IA")
    etiquetas = cfg.get("etiquetas", {}).get("jambo" if es_jambo(nombre, post) else "app", "")
    if etiquetas and post.get("app_slug") and canal == "tiktok":
        etiquetas += " #" + re.sub(r"[^a-z0-9]", "", post["app_slug"].lower())
    if etiquetas:
        cuerpo.append(etiquetas)
    return "\n".join(cuerpo)[:cfg.get("max_caracteres", 2100)]


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
        if cfg.get("solo_apps") and (es_jambo(nombre, post) or not post.get("app_slug")):
            continue
        piezas[nombre] = (post, res)
    orden = [n for n in cfg.get("orden_inicial", []) if n in piezas] + \
            [n for n in sorted(piezas) if n not in cfg.get("orden_inicial", [])]
    jambo = [n for n in orden if es_jambo(n, piezas[n][0])]
    apps = [n for n in orden if not es_jambo(n, piezas[n][0])]
    mezcla = []
    nj, na = cfg.get("mezcla", [2, 1])                 # p. ej. 2 de El Jambo por 1 de app
    while jambo or apps:
        mezcla += jambo[:nj]; jambo = jambo[nj:]
        mezcla += apps[:na]; apps = apps[na:]
    return [(n, *piezas[n]) for n in mezcla]


def huecos_libres(cfg, estado, ahora):
    ocupados = {v.get("dueAt") for v in estado.get("enviados", {}).values()}
    dia = ahora.astimezone(MADRID).date()
    for _ in range(60):
        for hhmm in (cfg["huecos"] if dia.isoweekday() in cfg.get("dias", [1, 2, 3, 4, 5, 6, 7]) else []):
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


def canal_buffer(cfg):
    """Id del canal en Buffer por nombre de servicio; None si el dueño aún no lo ha conectado."""
    for org in buffer("query { account { organizations { id name } } }")["account"]["organizations"]:
        canales = buffer('query { channels(input: {organizationId: %s}) { id name service } }' % json.dumps(org["id"]))
        for c in canales["channels"]:
            if cfg["servicio"] in str(c.get("service", "")).lower():
                return c["id"]
    return None


def gh(*args, check=True):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError("gh " + " ".join(args[:3]) + ": " + r.stderr.strip()[-300:])
    return r


def medio_publico(nombre, media_id, canal, cfg):
    """Instagram -> release «redes» (URL pública y estable para que Buffer la descargue). Vídeo o primer fotograma."""
    pub = leer(os.path.join(RAIZ, "equipo", "config_publico.json"), {})
    url = "https://graph.facebook.com/%s/%s?%s" % (pub.get("version", "v27.0"), media_id, urllib.parse.urlencode(
        {"fields": "media_url", "access_token": os.environ["PAGE_TOKEN"]}))
    with urllib.request.urlopen(url, timeout=60) as r:
        media = json.load(r).get("media_url")
    if not media:
        raise RuntimeError("Instagram no da media_url")
    fichero = "/tmp/%s_%s.mp4" % (canal, nombre)
    urllib.request.urlretrieve(media, fichero)
    if os.path.getsize(fichero) < 200_000:
        raise RuntimeError("vídeo descargado demasiado pequeño")
    if cfg["medio"] == "imagen":
        jpg = fichero[:-4] + ".jpg"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(cfg.get("fotograma_s", 0.6)), "-i", fichero,
                        "-frames:v", "1", "-vf", "scale=-2:1080,pad=1080:1080:(ow-iw)/2:0:color=0x071226",
                        "-q:v", "3", jpg], check=True)
        fichero = jpg
    if gh("release", "view", RELEASE, check=False).returncode != 0:
        gh("release", "create", RELEASE, "--title", "Medios para Buffer", "--notes", "Copias temporales para Buffer.")
    gh("release", "upload", RELEASE, fichero, "--clobber")
    return "https://github.com/%s/releases/download/%s/%s" % (REPO, RELEASE, os.path.basename(fichero))


def crear_post(id_canal, texto, url, cuando, post, canal, cfg):
    if cfg["medio"] == "imagen":
        medio = "{image: {url: %s}}" % json.dumps(url)
    else:
        medio = "{video: {url: %s, metadata: {thumbnailOffset: 0}}}" % json.dumps(url)
    meta = ""
    if canal == "tiktok":
        meta = ", metadata: {tiktok: {isAiGenerated: true}}"   # voz sintética: etiqueta oficial de IA de TikTok
    elif canal == "google":
        meta = ", metadata: {google: {type: whats_new, detailsWhatsNew: {button: signup, link: %s}}}" % json.dumps(
            enlace(post, canal))
    q = """mutation { createPost(input: {text: %s, channelId: %s, schedulingType: automatic, mode: customScheduled,
      dueAt: %s, assets: [%s]%s}) {
      ... on PostActionSuccess { post { id } } ... on MutationError { message } } }""" % (
        json.dumps(texto, ensure_ascii=False), json.dumps(id_canal), json.dumps(cuando), medio, meta)
    r = buffer(q)["createPost"]
    if not r.get("post"):
        raise RuntimeError("Buffer rechazó el post: " + str(r.get("message")))
    return r["post"]["id"]


def limpiar_release(estado, ahora):
    limite = (ahora - timedelta(days=3)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    for nombre, v in estado.get("enviados", {}).items():
        if v.get("dueAt", "9") < limite and not v.get("limpio"):
            gh("release", "delete-asset", RELEASE, v.get("fichero", ""), "-y", check=False)
            v["limpio"] = True


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    canal = args[0] if args else ""
    if canal not in ("tiktok", "linkedin", "google"):
        raise SystemExit("Uso: redes_buffer.py tiktok|linkedin|google [--simular]")
    simular = "--simular" in sys.argv
    carpeta = os.path.join(RAIZ, "equipo", canal)
    cfg = leer(os.path.join(carpeta, "config.json"), {})
    ruta_estado = os.path.join(carpeta, "estado.json")
    estado = leer(ruta_estado, {"enviados": {}, "ultimo_error": ""})
    ahora = datetime.now(timezone.utc)
    ahora_iso = ahora.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    pendientes = sum(1 for v in estado["enviados"].values() if v.get("dueAt", "") > ahora_iso)
    cupo = max(0, cfg["max_pendientes"] - pendientes)
    lista = candidatos(cfg, estado)
    print(f"{canal}: {pendientes} programados, cupo {cupo}, {len(lista)} piezas disponibles")
    if simular:
        for (nombre, post, _), cuando in zip(lista, huecos_libres(cfg, estado, ahora)):
            print(f"\n=== {nombre} · {cuando}\n{texto_canal(nombre, post, cfg, canal)}")
        return
    if not os.environ.get("BUFFER_API_KEY"):
        print(f"{canal} en espera: falta el secreto BUFFER_API_KEY (ver equipo/{canal}/LEEME.md).")
        return
    antes = json.dumps(estado, sort_keys=True)
    try:
        id_canal = canal_buffer(cfg)
        if not id_canal:
            print(f"{canal} en espera: Buffer no tiene ese canal conectado todavía.")
            return
        for (nombre, post, res), cuando in zip(lista[:cupo], huecos_libres(cfg, estado, ahora)):
            url = medio_publico(nombre, res["media_id"], canal, cfg)
            pid = crear_post(id_canal, texto_canal(nombre, post, cfg, canal), url, cuando, post, canal, cfg)
            estado["enviados"][nombre] = {"dueAt": cuando, "buffer_id": pid, "enviado": ahora_iso,
                                          "fichero": os.path.basename(url)}
            estado["ultimo_error"] = ""
            escribir(ruta_estado, estado)
            print(f"{nombre}: programado en {canal} para {cuando}")
    except Exception as e:                             # no tumba el workflow: queda anotado para el Supervisor
        estado["ultimo_error"] = f"{ahora_iso} · {e}"[:500]
        print(f"ERROR {canal}:", estado["ultimo_error"])
    limpiar_release(estado, ahora)
    if json.dumps(estado, sort_keys=True) != antes:
        escribir(ruta_estado, estado)


if __name__ == "__main__":
    main()
