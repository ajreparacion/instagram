#!/usr/bin/env python3
"""Creador vía API directa de Anthropic (piloto, 18/11/2026) — SOLO la parte mecánica.

El rol CREADOR completo (ver `equipo/roles/creador.md`) escribe guiones, decide episodios y
dispara renders reales en Neogest Studio a través del MCP de Base44 (`node scripts/render.mjs`,
`upload_app_asset`, `create_checkpoint`...). Ese MCP solo existe dentro de una sesión de Claude
Code: no hay forma limpia de llamarlo desde un script suelto con la API de Anthropic sin
construir una integración HTTP directa contra Base44 (token propio, subida de ficheros,
despliegue) que nadie ha pedido todavía. Por eso este piloto NO sustituye al Creador entero:
decisión documentada en equipo/tablon.md (18/11/2026) y en la PR de esta migración. Queda
pendiente de que el dueño decida si se construye esa integración (fase 2).

Lo que SÍ es mecánico y viable por API directa, y es lo que hace este script:
  - Piezas rechazadas por Calidad SOLO por motivos de texto/metadata del post.json (precio no
    autorizado, falta bloque `youtube`, falta `avance_siguiente`, cierre prohibido, atribución
    musical duplicada o incorrecta...) sin tocar el vídeo ni su render. Si el calidad.json
    mezcla motivos de vídeo (imagen, audio, estructura) con motivos de texto, el modelo solo
    toca el texto y dice en el tablón que el vídeo sigue pendiente de un render real.
  - Nunca cambia `renderizado`, `asset`, `video_externo`, `guion.json` ni `spec.json`: estos
    campos están fuera del esquema que la herramienta `escribir_post` acepta, así que el
    modelo no puede tocarlos aunque lo intente.

Variables de entorno: ANTHROPIC_API_KEY (secreto del repo).
Uso: python3 herramientas/creador_api.py
"""
import datetime
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COLA = os.path.join(RAIZ, "cola")
TABLON = os.path.join(RAIZ, "equipo", "tablon.md")
DIRECTIVA = os.path.join(RAIZ, "equipo", "DIRECTIVA_VIGENTE.md")
ROL = os.path.join(RAIZ, "equipo", "roles", "creador.md")

MODELO = "claude-sonnet-5"
MAX_PIEZAS = 4
MAX_TURNOS = 4

# Campos de post.json que este piloto tiene permiso para reescribir. Todo lo demás (render,
# vídeo, guion) queda fuera del esquema de la herramienta y no se puede tocar desde aquí.
CAMPOS_PERMITIDOS = {
    "texto", "youtube", "facebook", "avance_siguiente", "comentario_fijado",
    "monetizacion", "musica", "_nota_creador",
}


def _leer(ruta):
    if not os.path.exists(ruta):
        return ""
    with open(ruta, encoding="utf-8") as f:
        return f.read()


def _leer_json(ruta):
    if not os.path.isfile(ruta):
        return None
    try:
        return json.load(open(ruta, encoding="utf-8"))
    except Exception:
        return None


def piezas_rechazadas_por_texto():
    """Heurística determinista (sin API): piezas con calidad.json aprobado=false cuyos
    `motivos` parecen todos de texto/metadata (no mencionan vídeo, imagen, audio, pico, LUFS,
    silencio, plano, fotograma, motor...). Si hay duda, se incluye igualmente: el modelo decide
    y, si no puede arreglar nada de texto, lo dice sin escribir cambios."""
    claves_video = ("audio", "lufs", "pico", "db", "silencio", "imagen", "fotograma",
                     "plano", "motor", "render", "pixel", "resoluci", "encuadre", "voz ")
    candidatas = []
    if not os.path.isdir(COLA):
        return candidatas
    for pid in sorted(os.listdir(COLA)):
        pdir = os.path.join(COLA, pid)
        cal = _leer_json(os.path.join(pdir, "calidad.json"))
        post = _leer_json(os.path.join(pdir, "post.json"))
        if not cal or not post or cal.get("aprobado"):
            continue
        if cal.get("aprobado_por") == "dueño":
            continue
        motivos = cal.get("motivos") or []
        if not motivos:
            continue
        texto_motivos = " ".join(motivos).lower()
        solo_texto = not any(k in texto_motivos for k in claves_video)
        candidatas.append({"pid": pid, "motivos": motivos, "solo_texto": solo_texto,
                            "nota": cal.get("nota")})
    # primero las que parecen 100% de texto, para no gastar turnos en piezas que de todos
    # modos necesitan un render real
    candidatas.sort(key=lambda c: not c["solo_texto"])
    return candidatas


HERRAMIENTAS = [
    {
        "name": "escribir_post",
        "description": ("Reescribe SOLO los campos de texto/metadata indicados del post.json "
                         "de la pieza (no toca renderizado, asset, video_externo ni guion: no "
                         "están en este esquema). Pasa únicamente los campos que cambias."),
        "input_schema": {
            "type": "object",
            "properties": {
                "texto": {"type": "string"},
                "youtube": {"type": "object"},
                "facebook": {"type": "object"},
                "avance_siguiente": {"type": "string"},
                "comentario_fijado": {"type": "string"},
                "monetizacion": {"type": "object"},
                "musica": {"type": "object"},
                "nota_para_calidad": {"type": "string",
                                       "description": "qué has arreglado y qué sigue pendiente de vídeo"},
            },
            "required": ["nota_para_calidad"],
        },
    },
    {
        "name": "sin_arreglo_de_texto",
        "description": "Usa esto si, tras mirar los motivos, ninguno es arreglable sin tocar el vídeo.",
        "input_schema": {
            "type": "object",
            "properties": {"explicacion": {"type": "string"}},
            "required": ["explicacion"],
        },
    },
]


def _sistema():
    return (
        "Eres el rol CREADOR del equipo de redes de Neogest Lab, pero ejecutado vía API "
        "directa en un piloto deliberadamente reducido (ver cabecera de "
        "herramientas/creador_api.py): SOLO arreglas texto y metadata de post.json de piezas "
        "ya rechazadas por Calidad, nunca el vídeo ni su render. Te paso los `motivos` del "
        "rechazo y el post.json actual. Si algún motivo es de texto/metadata (precio no "
        "autorizado, falta bloque youtube, falta avance_siguiente, cierre prohibido, "
        "atribución musical incorrecta, afirmación sin fuente citada...), corrígelo con "
        "`escribir_post` pasando solo los campos que cambias, y dentro de `nota_para_calidad` "
        "explica qué arreglaste y qué sigue necesitando un render real (si lo hay). Si ningún "
        "motivo es de texto, llama a `sin_arreglo_de_texto`. No inventes cifras, precios, "
        "clientes ni fuentes: si falta la fuente real para arreglar algo, dilo en vez de "
        "improvisarla. No repitas textos ya usados en otras piezas que te enseño si los ves. "
        "Sigue el §5 (formatos) y §7 (publicación) de la directiva y tu rol de abajo.\n\n"
        "--- equipo/DIRECTIVA_VIGENTE.md (extracto completo) ---\n" + _leer(DIRECTIVA)
        + "\n\n--- equipo/roles/creador.md ---\n" + _leer(ROL)
    )


def arreglar_pieza(cliente, sistema, cand):
    pid = cand["pid"]
    pdir = os.path.join(COLA, pid)
    post = _leer_json(os.path.join(pdir, "post.json")) or {}
    cal = _leer_json(os.path.join(pdir, "calidad.json")) or {}
    mensaje = (
        f"Pieza: {pid}\n\nMotivos del rechazo (calidad.json, nota {cal.get('nota')}):\n"
        + json.dumps(cal.get("motivos"), ensure_ascii=False, indent=1)
        + "\n\ncomo_arreglarlo (si lo dejó Calidad):\n" + json.dumps(cal.get("como_arreglarlo", ""), ensure_ascii=False)
        + "\n\npost.json actual (completo):\n```json\n" + json.dumps(post, ensure_ascii=False, indent=1) + "\n```"
    )
    mensajes = [{"role": "user", "content": mensaje}]
    resultado = {"pid": pid, "escrito": False, "nota": ""}
    for _ in range(MAX_TURNOS):
        resp = cliente.messages.create(model=MODELO, max_tokens=2000, system=sistema,
                                        tools=HERRAMIENTAS, thinking={"type": "disabled"},
                                        messages=mensajes)
        mensajes.append({"role": "assistant", "content": resp.content})
        llamadas = [b for b in resp.content if getattr(b, "type", None) == "tool_use"]
        if not llamadas:
            textos = [b.text for b in resp.content if getattr(b, "type", None) == "text"]
            resultado["nota"] = "\n".join(textos).strip()[:400]
            break
        bloques = []
        for llamada in llamadas:
            if llamada.name == "escribir_post":
                cambios = {k: v for k, v in dict(llamada.input).items() if k in CAMPOS_PERMITIDOS}
                nota = llamada.input.get("nota_para_calidad", "")
                nuevo = dict(post)
                nuevo.update(cambios)
                ahora = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                previa = nuevo.get("_nota_creador", "")
                nuevo["_nota_creador"] = (previa + "\n" if previa else "") + f"{ahora} Creador (API): {nota}"
                with open(os.path.join(pdir, "post.json"), "w", encoding="utf-8") as f:
                    json.dump(nuevo, f, ensure_ascii=False, indent=2)
                resultado["escrito"] = True
                resultado["nota"] = nota[:300]
                post = nuevo
                bloques.append({"type": "tool_result", "tool_use_id": llamada.id,
                                 "content": "post.json actualizado"})
            elif llamada.name == "sin_arreglo_de_texto":
                resultado["nota"] = llamada.input.get("explicacion", "")[:300]
                bloques.append({"type": "tool_result", "tool_use_id": llamada.id, "content": "entendido"})
            else:
                bloques.append({"type": "tool_result", "tool_use_id": llamada.id,
                                 "content": "ERROR: herramienta desconocida", "is_error": True})
        mensajes.append({"role": "user", "content": bloques})
        if resultado["escrito"] or resultado["nota"]:
            break
    return resultado


def _linea_tablon(resultados, total_candidatas):
    ahora = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    if not total_candidatas:
        return f"{ahora} · Creador (API, piloto texto) · sin piezas rechazadas por motivos de texto · nada"
    if not resultados:
        return (f"{ahora} · Creador (API, piloto texto) · {total_candidatas} piezas rechazadas "
                f"pendientes, ninguna evaluada aún esta pasada (límite {MAX_PIEZAS}) · nada")
    partes = []
    for r in resultados:
        if r["escrito"]:
            partes.append(f"{r['pid']} arreglada: {r['nota']}")
        else:
            partes.append(f"{r['pid']} sin arreglo de texto: {r['nota']}")
    return (f"{ahora} · Creador (API, piloto texto) · revisadas {len(resultados)} de "
            f"{total_candidatas} piezas rechazadas: " + " · ".join(partes)
            + " · Calidad: reevaluar; Creador (Claude Code): sigue siendo quien renderiza de nuevo lo que necesite vídeo")


def main():
    try:
        import anthropic
    except ImportError:
        print("Falta el paquete anthropic (pip install anthropic)", file=sys.stderr)
        sys.exit(1)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Falta ANTHROPIC_API_KEY en el entorno", file=sys.stderr)
        sys.exit(1)

    candidatas = piezas_rechazadas_por_texto()
    resultados = []
    if candidatas:
        cliente = anthropic.Anthropic(api_key=api_key)
        sistema = _sistema()
        for cand in candidatas[:MAX_PIEZAS]:
            try:
                resultados.append(arreglar_pieza(cliente, sistema, cand))
            except Exception as e:
                resultados.append({"pid": cand["pid"], "escrito": False, "nota": f"error: {e}"})

    linea = _linea_tablon(resultados, len(candidatas))
    with open(TABLON, "a", encoding="utf-8") as f:
        f.write(linea + "\n")
    print(linea)


if __name__ == "__main__":
    main()
