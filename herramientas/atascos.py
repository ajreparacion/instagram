#!/usr/bin/env python3
"""DETECTOR DE ATASCOS (21/11/2026, orden del dueño: «no quiero más cuellos de botella»).

Recorre cola/ y clasifica cada pieza parada: qué la frena, desde cuándo, a qué rol le toca y cómo se arregla.
Escribe equipo/atascos.md (lo leen Supervisor, Creador, Calidad y Mejora al empezar su pasada) y devuelve la lista.
Uso: python3 herramientas/atascos.py [--json]
No toca ninguna pieza: solo diagnostica. Las reglas de reacción están en DIRECTIVA_VIGENTE.md §7 bis.
"""
import datetime as dt
import glob
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SALIDA = os.path.join(RAIZ, "equipo", "atascos.md")
UTC = dt.timezone.utc


def _j(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _fecha(s):
    try:
        t = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
        return t if t.tzinfo else t.replace(tzinfo=UTC)
    except Exception:
        return None


def diagnosticar(ahora=None):
    ahora = ahora or dt.datetime.now(UTC)
    out = []
    for d in sorted(glob.glob(os.path.join(RAIZ, "cola", "*", ""))):
        pid = os.path.basename(os.path.dirname(d))
        post = _j(os.path.join(d, "post.json"))
        if not isinstance(post, dict):
            out.append({"pieza": pid, "tipo": "sin_post", "rol": "Creador", "urgencia": 2,
                        "motivo": "carpeta sin post.json", "arreglo": "completar post.json o retirar la carpeta"})
            continue
        if post.get("tipo") in ("carrusel", "imagen", "historia"):
            continue
        cuando = _fecha(post.get("cuando"))
        horas = (cuando - ahora).total_seconds() / 3600 if cuando else None
        cal = _j(os.path.join(d, "calidad.json")) or {}
        guion = _j(os.path.join(d, "guion.json")) or {}
        rend = post.get("renderizado")
        r_t = _fecha(rend) if isinstance(rend, str) else None
        urg = 0 if horas is None else (3 if horas < 0 else 2 if horas < 24 else 1 if horas < 72 else 0)
        base = {"pieza": pid, "cuando": post.get("cuando"), "horas_para_salir": None if horas is None else round(horas, 1)}

        if cal.get("aprobado"):
            if horas is not None and horas < -1:
                out.append({**base, "tipo": "aprobada_vencida", "rol": "Supervisor", "urgencia": 3,
                            "motivo": "aprobada y con la hora pasada sin publicar",
                            "arreglo": "mirar registro.log (token, cuota) y lanzar ciclo.yml; si no hay hueco, mover «cuando»"})
            continue
        fallo = post.get("_control_audio_fallo") or {}
        if post.get("_error_render"):
            out.append({**base, "tipo": "render_fallido", "rol": "Mejora", "urgencia": max(urg, 2),
                        "motivo": str(post["_error_render"]).splitlines()[-1][:200],
                        "arreglo": "si el guion no tiene escenas es un episodio del estudio: poner video_externo; si no, arreglar el generador"})
            continue
        if fallo.get("bloqueos"):
            out.append({**base, "tipo": "control_audio", "rol": "Creador", "urgencia": max(urg, 1),
                        "motivo": "; ".join(fallo["bloqueos"])[:220],
                        "arreglo": "reescribir la frase (cifras en letra, nombre propio fuera de la 1.ª palabra) y renderizado:false; si es un falso positivo, Mejora ajusta control_audio.py"})
            continue
        if not r_t:
            externo = bool(post.get("video_externo"))
            sin_escenas = not guion.get("escenas")
            if externo:
                motivo, rol, arreglo = "esperando al ciclo (descarga del vídeo externo)", "Supervisor", "si pasa de 1 h, lanzar ciclo.yml"
            elif sin_escenas:
                motivo, rol, arreglo = "episodio del estudio sin vídeo: nadie lo ha renderizado en Neogest Studio", "Creador", \
                    "renderizar en Neogest Studio (herramientas/estudio/LEEME.md) y poner video_externo + renderizado:false"
            else:
                motivo, rol, arreglo = "pendiente de render del ciclo", "Supervisor", "si pasa de 1 h, lanzar ciclo.yml"
            out.append({**base, "tipo": "sin_render", "rol": rol, "urgencia": urg, "motivo": motivo, "arreglo": arreglo})
            continue
        c_t = _fecha(cal.get("fecha"))
        if not cal or (c_t and c_t < r_t):
            espera = (ahora - r_t).total_seconds() / 3600
            out.append({**base, "tipo": "sin_nota", "rol": "Calidad", "urgencia": max(urg, 2 if espera > 2 else 1),
                        "motivo": f"renderizada hace {espera:.1f} h sin calidad.json vigente",
                        "arreglo": "la Calidad (API) corre cada hora desde reloj.yml; si pasa de 2 h, lanzar calidad_api.yml a mano"})
            continue
        out.append({**base, "tipo": "rechazada", "rol": "Creador", "urgencia": urg, "nota": cal.get("nota"),
                    "motivo": "; ".join(cal.get("motivos") or [str(cal.get("comentario") or "")])[:260],
                    "arreglo": str(cal.get("como_arreglarlo") or "ver calidad.json")[:260]})
    out.sort(key=lambda x: (-x.get("urgencia", 0), x.get("horas_para_salir") if x.get("horas_para_salir") is not None else 9e9))
    return out


def escribir(lista, ahora=None):
    ahora = ahora or dt.datetime.now(UTC)
    nombres = {3: "URGENTE (hora pasada)", 2: "sale en < 24 h", 1: "sale en < 72 h", 0: "más adelante"}
    lin = ["# Atascos de la cola (generado por herramientas/atascos.py; no editar a mano)",
           f"Actualizado: {ahora.strftime('%Y-%m-%d %H:%M UTC')} · {len(lista)} piezas paradas.",
           "Regla (DIRECTIVA §7 bis): cada rol empieza su pasada por SUS filas de aquí, de arriba abajo.", ""]
    por_rol = {}
    for a in lista:
        por_rol[a["rol"]] = por_rol.get(a["rol"], 0) + 1
    lin.append("Por rol: " + ", ".join(f"{r} {n}" for r, n in sorted(por_rol.items())) if por_rol else "Sin atascos.")
    lin.append("")
    lin.append("| Urgencia | Pieza | Sale | Tipo | Rol | Motivo | Arreglo |")
    lin.append("|---|---|---|---|---|---|---|")
    for a in lista:
        esc = lambda s: str(s or "").replace("|", "/").replace("\n", " ")
        lin.append(f"| {nombres.get(a.get('urgencia', 0))} | {a['pieza']} | {esc(a.get('cuando'))} | {a['tipo']} | {a['rol']} | "
                   f"{esc(a.get('motivo'))} | {esc(a.get('arreglo'))} |")
    nuevo = "\n".join(lin) + "\n"
    try:   # solo reescribe si cambia algo más que la hora (el ciclo corre cada 15 min: sin commits vacíos)
        viejo = open(SALIDA, encoding="utf-8").read()
        quita = lambda t: "\n".join(x for x in t.splitlines() if not x.startswith("Actualizado:"))
        if quita(viejo) == quita(nuevo):
            return
    except OSError:
        pass
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(nuevo)


if __name__ == "__main__":
    l = diagnosticar()
    escribir(l)
    if "--json" in sys.argv:
        print(json.dumps(l, ensure_ascii=False, indent=1))
    else:
        for a in l:
            print(f"[{a.get('urgencia')}] {a['pieza']:<38} {a['tipo']:<16} {a['rol']:<10} {a.get('motivo','')[:90]}")
