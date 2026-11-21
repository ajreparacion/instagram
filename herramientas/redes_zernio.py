#!/usr/bin/env python3
"""Redes vía Zernio (API con documentación pública confirmada) — TERCERA vía de publicación en
TikTok, independiente de Buffer (caído por su propia incidencia el 21/11/2026) y de Metricool
(solo borradores, a la espera de confirmar tiktokData). El dueño ya tiene la cuenta @neogest.lab
conectada en Zernio (MCP, sesión del 21/11/2026) — mcp zernio, orden del dueño.

Uso: python3 herramientas/redes_zernio.py tiktok [--simular]

A diferencia de Metricool, la API de Zernio SÍ publica/programa de verdad (no solo borrador):
POST https://zernio.com/api/v1/posts con scheduledFor (fecha exacta) + platforms:[{platform,
accountId}]. Sin ajustes de tiktokSettings el post pasa validate_post sin avisos (comprobado en
vivo el 21/11/2026), así que no se fuerzan privacy_level/consentimientos a mano: si Zernio los
exige algún día, el error de la API lo dirá y se añade entonces (cero alucinaciones).

Reutiliza TAL CUAL la selección de piezas, el texto por canal y la subida a la release pública
«redes» de herramientas/redes_buffer.py (misma fuente de verdad, canal nuevo: equipo/zernio/).
No repite nunca lo que Buffer o Metricool ya mandaron a la misma cuenta de TikTok.

Secretos: ZERNIO_API_KEY (obligatorio; se crea una sola vez en https://zernio.com/dashboard/api-keys
y lo pega el dueño en el repo — ver equipo/zernio/LEEME.md). Sin él, o sin canal conectado, no hace
nada y termina bien: el canal queda en espera. --simular enseña qué enviaría, sin llamar a nada.
"""
import glob  # noqa: F401  (se usa dentro de candidatos(), importado vía redes_buffer)
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from redes_buffer import RAIZ, candidatos, huecos_libres, leer, escribir, texto_canal, medio_publico  # noqa: E402

ZERNIO = "https://zernio.com/api/v1"


def _pedir(metodo, ruta, api_key, cuerpo=None):
    req = urllib.request.Request(
        ZERNIO + ruta,
        data=json.dumps(cuerpo).encode("utf-8") if cuerpo is not None else None,
        method=metodo,
        headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"Zernio {metodo} {ruta}: HTTP {e.code} — {detalle}")


def cuenta_tiktok(api_key, usuario):
    """Id de la cuenta de TikTok conectada en Zernio por nombre de usuario; None si no está."""
    datos = _pedir("GET", "/accounts?platform=tiktok", api_key)
    for c in datos.get("accounts", datos if isinstance(datos, list) else []):
        if usuario.lstrip("@").lower() in str(c.get("username", "")).lower():
            return c.get("id") or c.get("_id")
    return None


def crear_post(api_key, account_id, texto, cuando_iso, url):
    cuerpo = {
        "content": texto,
        "mediaItems": [{"type": "video", "url": url}],
        "scheduledFor": cuando_iso,
        "platforms": [{"platform": "tiktok", "accountId": account_id}],
    }
    r = _pedir("POST", "/posts", api_key, cuerpo)
    pid = r.get("id") or (r.get("post") or {}).get("id") or (r.get("data") or {}).get("id")
    if not pid:
        raise RuntimeError(f"Zernio no confirmó el id del post creado: {json.dumps(r)[:300]}")
    return pid


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    canal = args[0] if args else ""
    if canal not in ("tiktok",):
        raise SystemExit("Uso: redes_zernio.py tiktok [--simular]  (de momento solo tiktok)")
    simular = "--simular" in sys.argv
    carpeta = os.path.join(RAIZ, "equipo", "zernio")
    cfg = leer(os.path.join(carpeta, "config.json"), {})
    ruta_estado = os.path.join(carpeta, "estado.json")
    estado = leer(ruta_estado, {"enviados": {}, "ultimo_error": ""})
    ahora = datetime.now(timezone.utc)
    ahora_iso = ahora.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    pendientes = sum(1 for v in estado["enviados"].values() if v.get("dueAt", "") > ahora_iso)
    cupo = max(0, cfg.get("max_pendientes", 8) - pendientes)
    # MISMA cuenta de TikTok que Buffer/Metricool (equipo/tiktok y equipo/metricool): nunca repetir
    # lo que ya se mandó por esas vías, para que las 3 vías sean respaldo/variedad, no duplicado.
    estado_buffer = leer(os.path.join(RAIZ, "equipo", canal, "estado.json"), {"enviados": {}})
    estado_metricool = leer(os.path.join(RAIZ, "equipo", "metricool", "estado.json"), {"enviados": {}})
    estado_para_elegir = {"enviados": {**estado_buffer.get("enviados", {}), **estado_metricool.get("enviados", {}),
                                        **estado["enviados"]}}
    lista = candidatos(cfg, estado_para_elegir)
    print(f"zernio/{canal}: {pendientes} programados, cupo {cupo}, {len(lista)} piezas disponibles")
    if simular:
        for (nombre, post, _), cuando in zip(lista, huecos_libres(cfg, estado, ahora)):
            print(f"\n=== {nombre} · {cuando}\n{texto_canal(nombre, post, cfg, canal)}")
        return
    api_key = os.environ.get("ZERNIO_API_KEY")
    if not api_key:
        print(f"zernio/{canal} en espera: falta el secreto ZERNIO_API_KEY (ver equipo/zernio/LEEME.md).")
        return
    antes = json.dumps(estado, sort_keys=True)
    try:
        account_id = cfg.get("account_id") or cuenta_tiktok(api_key, cfg.get("usuario", "neogest.lab"))
        if not account_id:
            print(f"zernio/{canal} en espera: esa cuenta no está conectada en Zernio todavía.")
            return
        for (nombre, post, res), cuando in zip(lista[:cupo], huecos_libres(cfg, estado, ahora)):
            url = medio_publico(nombre, res["media_id"], canal, cfg)
            pid = crear_post(api_key, account_id, texto_canal(nombre, post, cfg, canal), cuando, url)
            estado["enviados"][nombre] = {"dueAt": cuando, "zernio_id": pid, "enviado": ahora_iso,
                                          "fichero": os.path.basename(url)}
            estado["ultimo_error"] = ""
            escribir(ruta_estado, estado)
            print(f"{nombre}: programado en Zernio/{canal} para {cuando}")
    except Exception as e:
        estado["ultimo_error"] = f"{ahora_iso} · {e}"[:500]
        print(f"ERROR zernio/{canal}:", estado["ultimo_error"])
    if json.dumps(estado, sort_keys=True) != antes:
        escribir(ruta_estado, estado)


if __name__ == "__main__":
    main()
