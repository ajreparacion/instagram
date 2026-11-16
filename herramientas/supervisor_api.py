#!/usr/bin/env python3
"""Supervisor vía API directa de Anthropic (piloto, orden del dueño 16/11/2026).

Sustituye, para este rol, la tarea programada de Claude Code (que gasta límite semanal del
plan Max) por una llamada directa a la API de Anthropic (gasta los créditos de pago por uso
de la cuenta, separados del plan Max). Mismo rol, mismo horario (12:27 y 18:27 Madrid), mismo
modelo (Haiku) y mismo contrato de salida que `equipo/roles/supervisor.md`.

Alcance de este piloto v1 (deliberadamente reducido para no arriesgar el repo en vivo):
  - SÍ: lee el estado (tablón, pendiente_usuario, cola/*, registro.log) y escribe UNA línea
    de diagnóstico en `equipo/tablon.md`, igual que haría la tarea de Claude Code.
  - NO todavía: no edita `equipo/pendiente_usuario.md` ni lanza `gh workflow run ciclo.yml`.
    Si el modelo detecta algo que lo necesite, lo dice en la línea del tablón para que lo
    recoja la próxima pasada de Claude Code (Supervisor sigue también programado 1x/semana
    como respaldo de validación hasta confirmar varias pasadas seguidas sin fallos).

Variables de entorno: ANTHROPIC_API_KEY (secreto del repo).
Uso: python3 herramientas/supervisor_api.py
"""
import datetime
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLON = os.path.join(RAIZ, "equipo", "tablon.md")
PENDIENTE = os.path.join(RAIZ, "equipo", "pendiente_usuario.md")
ROL = os.path.join(RAIZ, "equipo", "roles", "supervisor.md")
LOG = os.path.join(RAIZ, "registro.log")
COLA = os.path.join(RAIZ, "cola")

MODELO = "claude-haiku-5-5"


def _leer(ruta, lineas=None):
    if not os.path.exists(ruta):
        return ""
    with open(ruta, encoding="utf-8") as f:
        txt = f.read()
    if lineas:
        return "\n".join(txt.splitlines()[-lineas:])
    return txt


def _piezas_cola():
    """Resumen determinista de cola/<id>/post.json + calidad.json (ahorra tokens: no se
    manda el JSON entero, solo los campos que mira el Supervisor)."""
    resumen = []
    if not os.path.isdir(COLA):
        return resumen
    for pid in sorted(os.listdir(COLA)):
        pdir = os.path.join(COLA, pid)
        post_p = os.path.join(pdir, "post.json")
        cal_p = os.path.join(pdir, "calidad.json")
        if not os.path.isfile(post_p):
            continue
        try:
            post = json.load(open(post_p, encoding="utf-8"))
        except Exception:
            continue
        cal = {}
        if os.path.isfile(cal_p):
            try:
                cal = json.load(open(cal_p, encoding="utf-8"))
            except Exception:
                pass
        resumen.append({
            "id": pid,
            "cuando": post.get("cuando"),
            "renderizado": post.get("renderizado"),
            "formato": post.get("formato"),
            "aprobado": cal.get("aprobado"),
            "nota": cal.get("nota"),
        })
    return resumen


def _contexto():
    ahora = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "ahora_utc": ahora,
        "tablon_ultimas_80": _leer(TABLON, 80),
        "pendiente_usuario": _leer(PENDIENTE),
        "piezas_cola": _piezas_cola(),
        "registro_log_ultimas_30": _leer(LOG, 30),
    }


def _llamar_api(rol_md, contexto):
    try:
        import anthropic
    except ImportError:
        print("Falta el paquete anthropic (pip install anthropic)", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Falta ANTHROPIC_API_KEY en el entorno", file=sys.stderr)
        sys.exit(1)

    cliente = anthropic.Anthropic(api_key=api_key)
    sistema = (
        "Eres el rol SUPERVISOR del equipo de redes de Neogest Lab. Sigue exactamente las "
        "instrucciones de tu archivo de rol de abajo, sección «Comprueba». NO edites "
        "pendiente_usuario.md ni lances workflows: eso lo hace otra pasada. "
        "Responde ÚNICAMENTE con la línea (o líneas, una por hallazgo real) que hay que "
        "añadir al final de equipo/tablon.md, en español de España, con el formato exacto:\n"
        '"AAAA-MM-DD HH:MM UTC · Supervisor (API) · qué hiciste o qué encontraste · qué '
        'necesitas y de qué rol (o «nada»)"\n'
        "Usa la hora `ahora_utc` del contexto (en UTC, sin convertir). No escribas nada más: "
        "ni explicaciones, ni markdown, ni comillas envolventes. Si no hay ningún problema de "
        "los 5 puntos de «Comprueba», responde con una sola línea que diga que todo va bien y "
        "termina en «nada».\n\n--- ARCHIVO DE ROL (equipo/roles/supervisor.md) ---\n" + rol_md
    )
    mensaje = (
        "Contexto de esta pasada (JSON):\n```json\n"
        + json.dumps(contexto, ensure_ascii=False, indent=1)
        + "\n```"
    )
    resp = cliente.messages.create(
        model=MODELO,
        max_tokens=1200,
        system=sistema,
        messages=[{"role": "user", "content": mensaje}],
    )
    textos = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
    if not textos:
        tipos = [getattr(b, "type", "?") for b in resp.content]
        print(f"Sin bloque de texto; stop_reason={resp.stop_reason} tipos={tipos}", file=sys.stderr)
    return "\n".join(textos).strip()


def main():
    rol_md = _leer(ROL)
    if not rol_md:
        print(f"No encuentro {ROL}", file=sys.stderr)
        sys.exit(1)
    contexto = _contexto()
    salida = _llamar_api(rol_md, contexto)
    # Limpieza defensiva: nos quedamos solo con líneas que ya empiezan por una fecha AAAA-MM-DD,
    # por si el modelo añade texto de sobra a pesar de las instrucciones.
    lineas = [l for l in salida.splitlines() if re.match(r"^\d{4}-\d{2}-\d{2} ", l.strip())]
    if not lineas:
        print("Respuesta del modelo sin líneas con el formato esperado, no se escribe nada:", file=sys.stderr)
        print(salida, file=sys.stderr)
        sys.exit(1)
    with open(TABLON, "a", encoding="utf-8") as f:
        for l in lineas:
            f.write(l.strip() + "\n")
    print("\n".join(lineas))


if __name__ == "__main__":
    main()
