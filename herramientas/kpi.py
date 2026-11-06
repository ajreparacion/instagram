#!/usr/bin/env python3
"""
kpi.py — Cuadro de mando semanal de @nosabesloquehasvisto (Fase 0 de equipo/monetizacion.md §5).

Lee estadisticas.json (y publicados/*/ para las duraciones) y escribe la tabla de KPI en Markdown.
Solo biblioteca estándar. Nunca inventa cifras: lo que no está en los datos sale como "n/d".

Uso:
  python3 herramientas/kpi.py                      # imprime la tabla (ventana: 7 días)
  python3 herramientas/kpi.py --dias 14            # otra ventana
  python3 herramientas/kpi.py --buzzfy kpi_buzzfy.json
        # añade las cifras que solo da Buzzfy/Instagram (alcance a no seguidores, clics en el enlace),
        # copiadas a mano por el Analista en un JSON:
        # {"fecha":"2026-11-06","dias":7,"alcance_no_seguidores_total":14,"alcance_total":22,
        #  "clics_enlace":0,"no_seguidores_por_reel":{"17996499894053316":null}}
  python3 herramientas/kpi.py --escribir           # además sustituye el bloque entre los marcadores
                                                   # <!-- KPI:INICIO --> y <!-- KPI:FIN --> de equipo/kpi_semanal.md

Objetivos de Fase 0 (monetizacion.md §5 y plan del Estratega): ver OBJETIVOS abajo.
"""
import argparse
import json
import os
import statistics
import sys
from datetime import datetime, timedelta, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESTADISTICAS = os.path.join(RAIZ, "estadisticas.json")
PUBLICADOS = os.path.join(RAIZ, "publicados")
KPI_MD = os.path.join(RAIZ, "equipo", "kpi_semanal.md")
INICIO_ENFOQUE = datetime(2026, 11, 5, 20, 0, tzinfo=timezone.utc)  # desde aquí son reels del enfoque nuevo

# Objetivos de Fase 0 (6-16/11/2026). Fuente: monetizacion.md §5 y aprendizajes.md (Estratega 5/11).
OBJETIVOS = {
    "seguidores_netos_dia": ("≥ 0 (dejar de perder); Fase 1: +5/día", 0.0),
    "alcance_no_seg_reel": ("≥ 150 (la mitad de los 300 de alcance meta por reel)", 150),
    "alcance_reel": ("mediana ≥ 100 a 48 h en los 10 reels (decisión del 16/11); meta ≥ 300", 100),
    "compartidos_reel": ("≥ 3 por reel", 3),
    "guardados_reel": ("≥ 2 por reel", 2),
    "clics_enlace_semana": ("enlace activo al hub; Fase 1: 20/semana", 1),
    "visualizacion_media_s": ("≥ 15 s", 15),
    "pct_visto": ("≥ 50 % del reel", 50),
}


def leer_json(ruta, defecto=None):
    try:
        with open(ruta, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return defecto


def fecha(s):
    s = s.replace("Z", "+00:00")
    if len(s) >= 5 and s[-5] in "+-" and ":" not in s[-5:]:
        s = s[:-2] + ":" + s[-2:]
    d = datetime.fromisoformat(s)
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d


def duraciones_publicadas():
    """media_id -> duración del vídeo en s, a partir de locucion.json o guion.json de publicados/."""
    out = {}
    if not os.path.isdir(PUBLICADOS):
        return out
    for carpeta in sorted(os.listdir(PUBLICADOS)):
        ruta = os.path.join(PUBLICADOS, carpeta)
        res = leer_json(os.path.join(ruta, "resultado.json"), {}) or {}
        mid = res.get("media_id")
        if not mid:
            continue
        dur = None
        loc = leer_json(os.path.join(ruta, "locucion.json"))
        if isinstance(loc, list) and loc:
            try:
                dur = max(float(x.get("inicio", 0)) + float(x.get("duracion", 0)) for x in loc)
            except (TypeError, ValueError):
                dur = None
        if dur is None:
            g = leer_json(os.path.join(ruta, "guion.json"))
            if isinstance(g, dict) and g.get("escenas"):
                try:
                    dur = sum(float(e.get("duracion", 0)) for e in g["escenas"])
                except (TypeError, ValueError):
                    dur = None
        if dur:
            out[str(mid)] = dur
    return out


def fmt(v, dec=1, suf=""):
    if v is None:
        return "n/d"
    if isinstance(v, float):
        s = f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        s = f"{v:,}".replace(",", ".")
    return s + suf


def media(xs):
    xs = [x for x in xs if x is not None]
    return statistics.fmean(xs) if xs else None


def mediana(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def calcular(est, dias, buzzfy=None):
    ahora = fecha(est.get("actualizado")) if est.get("actualizado") else datetime.now(timezone.utc)
    desde = ahora - timedelta(days=dias)
    posts = est.get("posts", [])
    ventana = [p for p in posts if fecha(p["timestamp"]) >= desde and fecha(p["timestamp"]) >= INICIO_ENFOQUE
               and p.get("media_product_type") == "REELS"]
    todos30 = [p for p in posts if p.get("media_product_type") == "REELS" and p.get("metricas")]
    durs = duraciones_publicadas()

    def m(p, k):
        v = (p.get("metricas") or {}).get(k)
        return v if isinstance(v, (int, float)) else None

    filas_reel = []
    for p in ventana:
        avg = m(p, "ig_reels_avg_watch_time")
        avg_s = avg / 1000 if avg is not None else None
        dur = durs.get(str(p["id"]))
        pct = (avg_s / dur * 100) if (avg_s is not None and dur) else None
        edad_h = (ahora - fecha(p["timestamp"])).total_seconds() / 3600
        filas_reel.append({
            "id": p["id"], "fecha": fecha(p["timestamp"]).astimezone(timezone(timedelta(hours=1))).strftime("%d/%m %H:%M"),
            "edad_h": edad_h, "provisional": edad_h < 48,
            "alcance": m(p, "reach"), "views": m(p, "views"), "compartidos": m(p, "shares"),
            "guardados": m(p, "saved"), "comentarios": m(p, "comments"), "likes": m(p, "likes"),
            "avg_s": avg_s, "dur": dur, "pct": pct,
            "no_seg": (buzzfy or {}).get("no_seguidores_por_reel", {}).get(str(p["id"])),
        })

    # Seguidores netos/día desde historial_cuenta (primer y último punto de la ventana)
    hist = sorted(est.get("historial_cuenta", []), key=lambda h: h["fecha"])
    hist_v = [h for h in hist if fecha(h["fecha"]) >= desde]
    netos_dia = None
    netos_detalle = "sin historial suficiente"
    if len(hist_v) >= 2:
        d_dias = (fecha(hist_v[-1]["fecha"]) - fecha(hist_v[0]["fecha"])).total_seconds() / 86400
        if d_dias > 0:
            netos_dia = (hist_v[-1]["seguidores"] - hist_v[0]["seguidores"]) / d_dias
            netos_detalle = f"{hist_v[0]['seguidores']} → {hist_v[-1]['seguidores']} en {d_dias:.1f} días"
    if buzzfy and buzzfy.get("seguidores_netos_dia") is not None:
        netos_dia = buzzfy["seguidores_netos_dia"]
        netos_detalle = f"Buzzfy ig_follower_growth ({buzzfy.get('fecha', '')})"

    ref30 = {
        "alcance": mediana([m(p, "reach") for p in todos30]),
        "compartidos": mediana([m(p, "shares") for p in todos30]),
        "guardados": mediana([m(p, "saved") for p in todos30]),
        "avg_s": mediana([m(p, "ig_reels_avg_watch_time") / 1000 for p in todos30 if m(p, "ig_reels_avg_watch_time") is not None]),
    }

    alcance_no_seg_reel = None
    if buzzfy and buzzfy.get("alcance_no_seguidores_total") is not None and filas_reel:
        alcance_no_seg_reel = buzzfy["alcance_no_seguidores_total"] / len(filas_reel)
    clics = buzzfy.get("clics_enlace") if buzzfy else None

    kpis = [
        ("Seguidores netos / día", netos_dia, OBJETIVOS["seguidores_netos_dia"][0], f"historial_cuenta: {netos_detalle}", 2),
        ("Alcance a no seguidores / reel", alcance_no_seg_reel, OBJETIVOS["alcance_no_seg_reel"][0],
         "solo Buzzfy (ig_account_stats reach.nonFollowers ÷ reels de la ventana); n/d si no se pasa --buzzfy", 1),
        ("Alcance / reel (media · mediana)", media([f["alcance"] for f in filas_reel]), OBJETIVOS["alcance_reel"][0],
         f"metricas.reach; mediana ventana {fmt(mediana([f['alcance'] for f in filas_reel]))}; referencia 30 últimos {fmt(ref30['alcance'])}", 1),
        ("Compartidos / reel", media([f["compartidos"] for f in filas_reel]), OBJETIVOS["compartidos_reel"][0],
         f"metricas.shares; referencia 30 últimos (mediana) {fmt(ref30['compartidos'])}", 2),
        ("Guardados / reel", media([f["guardados"] for f in filas_reel]), OBJETIVOS["guardados_reel"][0],
         f"metricas.saved; referencia 30 últimos (mediana) {fmt(ref30['guardados'])}", 2),
        ("Clics en el enlace / semana", clics, OBJETIVOS["clics_enlace_semana"][0],
         "solo Buzzfy (ig_account_stats profileActivity.websiteClicks + linkTaps)", 0),
        ("Visualización media (s)", media([f["avg_s"] for f in filas_reel]), OBJETIVOS["visualizacion_media_s"][0],
         f"ig_reels_avg_watch_time ÷ 1000; referencia 30 últimos (mediana) {fmt(ref30['avg_s'])} s", 1),
        ("% visto (vis. media ÷ duración)", media([f["pct"] for f in filas_reel]), OBJETIVOS["pct_visto"][0],
         "duración de publicados/*/locucion.json o guion.json; n/d si la carpeta no los conserva", 1),
    ]
    return {"ahora": ahora, "dias": dias, "reels": filas_reel, "kpis": kpis, "ref30": ref30, "n30": len(todos30),
            "buzzfy": buzzfy}


def tabla(r):
    L = []
    prov = any(f["provisional"] for f in r["reels"])
    L.append(f"Actualizado con estadisticas.json de {r['ahora'].strftime('%d/%m/%Y %H:%M')} UTC · ventana {r['dias']} días · "
             f"{len(r['reels'])} reel(s) del enfoque nuevo" + (" · PROVISIONAL: hay reels con < 48 h" if prov else ""))
    if r["buzzfy"]:
        L.append(f"Cifras de Buzzfy copiadas a mano el {r['buzzfy'].get('fecha', 'n/d')} (ventana {r['buzzfy'].get('dias', 'n/d')} días).")
    L.append("")
    L.append("| KPI | Valor actual | Objetivo Fase 0 | Cómo se calcula |")
    L.append("|---|---|---|---|")
    for nombre, valor, obj, como, dec in r["kpis"]:
        v = fmt(valor, dec) if isinstance(valor, float) else fmt(valor)
        if nombre.startswith("% visto") and valor is not None:
            v += " %"
        L.append(f"| {nombre} | {v} | {obj} | {como} |")
    L.append("")
    if r["reels"]:
        L.append("| Reel | Publicado (CET) | Edad | Alcance | Repr. | Comp. | Guard. | Coment. | Vis. media | Duración | % visto |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for f in r["reels"]:
            edad = f"{f['edad_h']:.0f} h" + (" (prov.)" if f["provisional"] else "")
            L.append(f"| {f['id']} | {f['fecha']} | {edad} | {fmt(f['alcance'])} | {fmt(f['views'])} | {fmt(f['compartidos'])} | "
                     f"{fmt(f['guardados'])} | {fmt(f['comentarios'])} | {fmt(f['avg_s'], 1, ' s')} | {fmt(f['dur'], 1, ' s')} | "
                     f"{fmt(f['pct'], 0, ' %')} |")
    else:
        L.append("Sin reels del enfoque nuevo en la ventana.")
    L.append("")
    L.append(f"Referencia: mediana de los {r['n30']} reels de estadisticas.json — alcance {fmt(r['ref30']['alcance'])}, "
             f"compartidos {fmt(r['ref30']['compartidos'])}, guardados {fmt(r['ref30']['guardados'])}, "
             f"visualización media {fmt(r['ref30']['avg_s'])} s.")
    return "\n".join(L)


def escribir_md(texto):
    ini, fin = "<!-- KPI:INICIO -->", "<!-- KPI:FIN -->"
    try:
        with open(KPI_MD, encoding="utf-8") as f:
            md = f.read()
    except OSError:
        sys.exit(f"No existe {KPI_MD}")
    a, b = md.find(ini), md.find(fin)
    if a < 0 or b < 0 or b < a:
        sys.exit("kpi_semanal.md no tiene los marcadores KPI:INICIO / KPI:FIN")
    nuevo = md[: a + len(ini)] + "\n" + texto + "\n" + md[b:]
    with open(KPI_MD, "w", encoding="utf-8") as f:
        f.write(nuevo)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dias", type=int, default=7)
    ap.add_argument("--buzzfy", help="JSON con cifras de Buzzfy copiadas a mano")
    ap.add_argument("--escribir", action="store_true", help="actualiza el bloque de equipo/kpi_semanal.md")
    ap.add_argument("--estadisticas", default=ESTADISTICAS)
    args = ap.parse_args()
    est = leer_json(args.estadisticas)
    if not est:
        sys.exit(f"No se puede leer {args.estadisticas}")
    bz = leer_json(args.buzzfy) if args.buzzfy else None
    if args.buzzfy and bz is None:
        sys.exit(f"No se puede leer {args.buzzfy}")
    r = calcular(est, args.dias, bz)
    t = tabla(r)
    print(t)
    if args.escribir:
        escribir_md(t)
        print(f"\nActualizado {KPI_MD}", file=sys.stderr)


if __name__ == "__main__":
    main()
