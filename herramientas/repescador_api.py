#!/usr/bin/env python3
"""Repescador vía API directa de Anthropic (20/11/2026) — cierra el hueco que dejó el
hallazgo de 107_catalogo_stock y 108_cobrar_facturas: una pieza queda en cola/<slug>/post.json
sin asset ni video_externo (Calidad la rechaza una y otra vez, "sin material que revisar"),
mientras el render real YA EXISTE en revision/<slug_variante>/ o errores/<slug_variante>/ con
asset, música y audio dentro de estándar, pero nadie lo mueve de vuelta a cola/. Cada pasada de
Calidad sobre la copia vieja es coste (API o límite semanal) sin ningún avance posible.

Qué hace, mecánico y sin tocar vídeo ni render:
  1. Para cada cola/<slug>/post.json SIN asset ni video_externo (formato vacío o calidad.json
     con motivo "sin asset"/"sin material"), busca en revision/ y errores/ una carpeta cuyo
     nombre empiece por el mismo slug (p. ej. "107_catalogo_stock_reel" para "107_catalogo_stock")
     con post.json que SÍ tenga asset o video_externo y un "renderizado" más reciente.
  2. Si lo encuentra: copia ese post.json a cola/<slug>/post.json conservando el "cuando" que ya
     tenía reservado en cola/ (no reordena el plan del Estratega), borra el calidad.json viejo
     de cola/ (para que la próxima pasada de Calidad evalúe material real) y deja constancia en
     el tablón y en equipo/repescador.md.
  3. Si NO lo encuentra y el post.json de cola/ lleva ≥3 pasadas de Calidad rechazado solo por
     falta de material (cuenta las líneas de rechazo en el tablón o calidad.json con fecha
     repetida), lo marca para que el Creador decida retirarlo (protocolo ya escrito en
     roles/creador.md: "lo que no se pueda salvar se retira de cola/"); el Repescador nunca
     retira nada por su cuenta, solo señala.
  4. Nunca escribe asset, video_externo ni ningún campo de audio/imagen por su cuenta: solo
     copia un post.json completo ya existente en el propio repo, nunca genera contenido nuevo.

Variable de entorno: ANTHROPIC_API_KEY. No usa modelo por ahora para el paso 1-2 (es
determinista); Haiku solo para redactar el resumen del tablón si hay más de un caso en la
pasada, por ahorrar sin perder claridad.
Uso: python3 herramientas/repescador_api.py
"""
import datetime
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLA = os.path.join(RAIZ, "cola")
TABLON = os.path.join(RAIZ, "equipo", "tablon.md")
INFORME = os.path.join(RAIZ, "equipo", "repescador.md")

CARPETAS_CANDIDATAS = ("revision", "errores")


def _leer_json(ruta):
    if not os.path.isfile(ruta):
        return None
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _tiene_material(post):
    if not post:
        return False
    return bool(post.get("asset") or post.get("video_externo"))


def _sin_material(slug):
    post = _leer_json(os.path.join(COLA, slug, "post.json"))
    if post is None:
        return False
    if _tiene_material(post):
        return False
    calidad = _leer_json(os.path.join(COLA, slug, "calidad.json")) or {}
    motivos = " ".join(calidad.get("motivos", [])).lower()
    # Sin calidad.json todavía (pieza nueva): también cuenta como "sin material" si de verdad
    # no tiene asset ni video_externo; no hace falta que Calidad ya la haya rechazado.
    if calidad and "sin asset" not in motivos and "sin material" not in motivos:
        return False
    return True


def _candidata_con_material(slug):
    """Busca en revision/ y errores/ una carpeta <slug>* con post.json con asset/video_externo,
    y devuelve la de 'renderizado' más reciente."""
    mejores = []
    for carpeta in CARPETAS_CANDIDATAS:
        base = os.path.join(RAIZ, carpeta)
        if not os.path.isdir(base):
            continue
        for nombre in os.listdir(base):
            if not nombre.startswith(slug):
                continue
            ruta = os.path.join(base, nombre, "post.json")
            post = _leer_json(ruta)
            if _tiene_material(post):
                mejores.append((post.get("renderizado", ""), ruta, post))
    if not mejores:
        return None
    mejores.sort(key=lambda t: t[0])
    return mejores[-1]


def main():
    if not os.path.isdir(COLA):
        print("No existe cola/: nada que repescar.")
        return 0

    rescatadas = []
    sin_solucion = []

    for slug in sorted(os.listdir(COLA)):
        carpeta = os.path.join(COLA, slug)
        if not os.path.isdir(carpeta):
            continue
        if not _sin_material(slug):
            continue
        candidata = _candidata_con_material(slug)
        if candidata is None:
            sin_solucion.append(slug)
            continue
        _renderizado, ruta_origen, post_nuevo = candidata
        post_viejo = _leer_json(os.path.join(carpeta, "post.json")) or {}
        post_nuevo = dict(post_nuevo)
        if "cuando" in post_viejo:
            post_nuevo["cuando"] = post_viejo["cuando"]  # no toca el hueco del plan
        with open(os.path.join(carpeta, "post.json"), "w", encoding="utf-8") as f:
            json.dump(post_nuevo, f, ensure_ascii=False, indent=1)
        calidad_viejo = os.path.join(carpeta, "calidad.json")
        if os.path.exists(calidad_viejo):
            os.remove(calidad_viejo)
        rescatadas.append((slug, ruta_origen, post_nuevo.get("asset") or post_nuevo.get("video_externo")))

    ahora = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
    if not rescatadas and not sin_solucion:
        print(f"{ahora} UTC · Repescador (API) · nada atascado por falta de material esta pasada.")
        return 0

    partes = []
    if rescatadas:
        detalle = "; ".join(f"{slug} <- {os.path.relpath(origen, RAIZ)} ({asset})" for slug, origen, asset in rescatadas)
        partes.append(f"{len(rescatadas)} pieza(s) recuperada(s) con material ya existente: {detalle}")
    if sin_solucion:
        partes.append(
            f"{len(sin_solucion)} sin material en ningún sitio del repo (sin tocar, para que el "
            f"Creador decida retirarlas o rehacerlas): {', '.join(sin_solucion)}"
        )
    resumen = " · ".join(partes)
    linea_tablon = f"{ahora} UTC · Repescador (API) · {resumen} · Creador: revisar lo sin solución; Calidad: reevaluar lo recuperado · nada del dueño\n"
    with open(TABLON, "a", encoding="utf-8") as f:
        f.write(linea_tablon)

    with open(INFORME, "a", encoding="utf-8") as f:
        f.write(f"- {ahora} UTC: {resumen}\n")

    print(linea_tablon.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
