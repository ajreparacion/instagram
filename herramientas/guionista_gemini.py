#!/usr/bin/env python3
"""Guionista de El Jambo que sabe vía API de Gemini (orden del dueño, 17/11/2026).

Motivo: el dueño ha visto lo publicado y los guiones no engachan ("no tiene sentido").
Hasta ahora el Creador escribía el guion él mismo (Sonnet) dentro de su pasada. Este script
pide los guiones a Gemini como un paso aparte, ANTES de cada pasada del Creador (09:51 y
15:51 Madrid), apoyándose en la biblia de la serie, los motivos de rechazo de Calidad y los
patrones de reels virales ya estudiados, para que lleguen con más gancho y lógica.

No sustituye al Creador: deja borradores en equipo/guiones_gemini/pendientes/ y es el
Creador quien elige, ajusta (decorado, hora, clip de la Biblioteca) y pone en cola/. Si
Gemini falla o no hay clave, no rompe nada: el Creador sigue pudiendo escribir el guion él
mismo como hasta ahora.

Variable de entorno: GEMINI_API_KEY (secreto del repo; cuenta darbish, capa gratis de
Google AI Studio). Uso: python3 herramientas/guionista_gemini.py [n_guiones]
"""
import datetime
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BIBLIA = os.path.join(RAIZ, "equipo", "serie_jambo.md")
LECCIONES = os.path.join(RAIZ, "equipo", "lecciones_calidad.md")
VIRALES = os.path.join(RAIZ, "equipo", "virales_semana.md")
TABLON = os.path.join(RAIZ, "equipo", "tablon.md")
COLA = os.path.join(RAIZ, "cola")
PENDIENTES = os.path.join(RAIZ, "equipo", "guiones_gemini", "pendientes")

# Lista de modelos a probar en orden (el primero que responda gana). gemini-2.0-flash dejó
# de estar disponible el 17/11/2026; comprobado ese día con herramientas/gemini_modelos.py
# qué acepta generateContent la clave real. gemini-3.8-flash y gemini-flash-latest dieron 503
# (saturados) y gemini-2.5-flash/gemini-2.5-flash-lite dieron 404 "no disponible para cuentas
# nuevas" con esta clave: se dejan de últimos por si cambia. Lista larga a propósito para
# aguantar baches de saturación sin dejar de producir guiones.
MODELOS = [
    "gemini-3.7-flash",
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-3.5-flash",
    "gemini-2.5-flash",
]
N_POR_DEFECTO = 4
PERSONAJES_VALIDOS = {"rosa", "felipe", "sindy", "neo", "cliente", "conchaqueton"}
ESTILOS_VALIDOS = {"gancho", "gag", "remate", "cierre"}
# 19/11/2026: rechazo mecánico de lo que más se parece a "declaración de postura" en vez de
# una frase hablada con golpe cómico (el fallo real que el dueño señaló). No es perfecto
# (no distingue una frase larga pero graciosa), pero descarta el patrón más repetido.
PATRON_ARGUMENTO = re.compile(
    r"\b(no debería|debería|no tiene por qué|no tendría que|tendría que|no debe|"
    r"es (un|una) (derecho|obligación|falta de respeto)|eso (no )?es justo)\b",
    re.IGNORECASE,
)
MAX_PALABRAS_GAG = 14


def _leer(ruta, lineas=None):
    if not os.path.exists(ruta):
        return ""
    with open(ruta, encoding="utf-8") as f:
        txt = f.read()
    if lineas:
        return "\n".join(txt.splitlines()[-lineas:])
    return txt


def _temas_recientes():
    """Slugs/temas ya en cola o publicados recientemente, para que Gemini no repita
    situación (ahorra una ronda de rechazo por duplicado)."""
    temas = []
    for carpeta in ("cola", "publicados", "revision"):
        ruta = os.path.join(RAIZ, carpeta)
        if os.path.isdir(ruta):
            temas.extend(sorted(os.listdir(ruta))[-15:])
    return temas


def _prompt(n):
    biblia = _leer(BIBLIA)
    lecciones = _leer(LECCIONES, lineas=25)
    virales = _leer(VIRALES, lineas=60)
    temas = ", ".join(_temas_recientes()) or "(ninguno todavía)"

    esquema = {
        "slug": "texto-corto-sin-espacios, 2-4 palabras, nueva situación",
        "set": "oficina | despacho | bar | calle | reunion (el set de las escenas de diálogo; el plano de casa de apertura/cierre lo pone el código, no va aquí)",
        "hora": "entero 0-23 (hora del día de la escena)",
        "flow": "null (de momento sin vídeo real; si algún día hay un clip de b-roll de fachada de barrio ya generado, aquí va su URL; si es null se usa el set vectorial 'casa' para el plano de apertura/cierre)",
        "moraleja": "6-9 palabras, tono serio, el mensaje que se queda; si hay una cifra de la tabla de la biblia que encaje, inclúyela",
        "recuerdo": "6-12 palabras, una línea que conecta con un episodio anterior ya publicado (de los temas ya usados) — un personaje menciona o reacciona a algo que pasó en otro capítulo; null si no hay ninguno con el que conectar todavía",
        "bucle_visual": "en 4-8 palabras, qué elemento o encuadre del gancho se repite tal cual en el cierre (misma pose, mismo plano o mismo objeto) para que el vídeo pueda volver a verse en bucle sin notar el corte",
        "escenas": [
            {
                "e": "gancho",
                "h": "rosa",
                "t": "texto exacto que dice o el texto en pantalla, máx 8 palabras, situación reconocible desde el fotograma 0 (visible en los primeros 0,5 s, antes incluso de que se lea el texto entero)",
            },
            {"e": "gag", "h": "felipe|sindy", "t": "frase del golpe 1 de la escalada, registro de barrio con réplica inteligente"},
            {"e": "gag", "h": "rosa", "t": "frase del golpe 2, peor que el 1"},
            {"e": "gag", "h": "felipe|sindy", "t": "frase del golpe 3, peor que el 2, remata con 'Que lo resuelva el Neo'"},
            {"e": "remate", "h": "neo", "t": "frase del giro: Neo resuelve ESE conflicto y deja a Rosa en evidencia"},
            {"e": "cierre", "h": "neo", "t": "texto en pantalla, debe coincidir o repetir la moraleja, y su último fotograma debe poder encadenar con el gancho (ver bucle_visual) para que al repetirse el vídeo no se note la costura"},
        ],
    }

    return f"""Eres el guionista de la serie de humor "El Jambo que sabe" (Instagram @neogestlab,
Neogest Lab). Español de España, humor negro y satírico contra la cultura del trabajo y la
burocracia, NUNCA contra personas reales, colectivos ni marcas. Escribe {n} guiones de
episodio NUEVOS, cada uno con un conflicto y una situación distintos entre sí y distintos de
los temas ya usados: {temas}.

BIBLIA DE LA SERIE (personajes, tono, estructura, cifras verificadas que puedes citar si
encajan de verdad; no inventes cifras nuevas):
---
{biblia}
---

MOTIVOS DE RECHAZO MÁS REPETIDOS por el equipo de Calidad en las últimas piezas (evítalos
todos; son la razón por la que el dueño ha pedido este cambio, dice que "los guiones no
engachan, no tiene sentido"):
---
{lecciones}
---

PATRONES DE REELS VIRALES ya estudiados en el nicho (cópialos en estructura, nunca en
contenido ni frases literales):
---
{virales}
---

AVISO DE CALIDAD REAL (esto es lo que el dueño está señalando ahora mismo, 19/11: "tienen
que ser de gran calidad"): el validador automático solo comprueba la FORMA (número de
escenas, personajes válidos, longitud de la moraleja); nunca ha comprobado si el chiste
funciona, así que no te confíes de que "pasa" signifique que es bueno. El fallo que más se
repite en los borradores recientes es que cada "gag" es una DECLARACIÓN DE POSTURA (alguien
defendiendo una opinión, tipo debate o panfleto: "el compromiso familiar no debería tener
precio alguno") en vez de una REACCIÓN HABLADA natural con timing cómico. Eso no hace reír.
  MAL (declaración, prohibido): "El compromiso familiar no debería tener precio alguno."
  BIEN (reacción con golpe): "Ya puestos, tráete también a mi suegra, que así hacemos piña."
Cada gag debe sonar a algo que alguien realmente suelta en voz alta al oír la frase
anterior (ironía, sarcasmo, la consecuencia absurda llevada un paso más lejos), nunca a un
argumento razonado. Si al leerlo en voz alta suena a artículo de opinión, está mal escrito:
reescríbelo como lo diría una persona enfadada o resignada en ese momento.

QUÉ ES REALMENTE HUMOR NEGRO (orden del dueño, 20/11: "no lo he visto en ningún momento";
tiene razón, lo que se ha escrito hasta ahora es ironía y sarcasmo de oficina, no humor
negro). La diferencia no es de TEMA, es de TONO: el sarcasmo se queja de lo injusto con
gracia (indignación disfrazada de chiste); el humor negro trata lo injusto o lo cruel con
la misma frialdad y naturalidad con que se trataría algo trivial, sin indignarse ni
suavizarlo — la gracia está en esa distancia fría, no en la queja. Las líneas rojas de la
biblia siguen mandando (nunca suicidio, autolesión, enfermedad o muerte real, ni contra
personas o colectivos reales): el humor negro aquí no viene de tocar esos temas, viene del
FATALISMO, la resignación sin drama y la crueldad del sistema contada como lo más normal
del mundo.
  MAL (esto es sarcasmo, no humor negro — es lo que lleva saliendo hasta ahora): "Ya puestos,
  tráete también a mi suegra, que así hacemos piña." (el personaje se indigna con gracia;
  sigue siendo una queja, solo que ingeniosa).
  BIEN (humor negro real: frialdad total ante algo injusto, dicho sin ninguna sorpresa ni
  indignación, como un hecho ya asumido): "Si me despiden mañana, lo único que cambia es que
  dejo de fingir que me importa." / "Lo normal es que esto salga mal. Lleva así tres años, no
  es nada nuevo."
Pista rápida para saber si un gag es de verdad humor negro: léelo en voz alta con cara de
póker, sin ánimo de queja. Si solo funciona gritado o indignado, es sarcasmo (válido, pero
no es lo que se pide ahora); si funciona dicho en plano, con total indiferencia, es humor
negro. Al menos uno de los tres golpes de cada episodio debe ser de este segundo tipo.
Dato real de rendimiento (virales_semana.md, visto el 16/11): lo que mejor ha funcionado en
la cuenta hasta ahora son los episodios de cliente/jefe con una situación reconocible desde
la primera línea y, sobre todo, los que tienen "Parte 2" (continuidad: alguien pregunta
"¿y qué pasó con...?" y el episodio responde). Los temas de oficina genéricos sin ese gancho
reconocible son los que menos vistas sacan. Cuando puedas, prefiere una situación que un
espectador reconozca de inmediato por haberla vivido, y considera si el conflicto de hoy
podría tener una "Parte 2" natural para otro episodio (dilo en el slug con "_parte2" si es
la continuación de un tema ya usado: {temas}).

GANCHO DE MEDIO SEGUNDO Y VÍDEO EN BUCLE (orden del dueño, 20/11, "vídeos completamente
adictivos"): no basta con que el gancho tenga ≤ 8 palabras, tiene que entenderse la situación
SOLO con la imagen en los primeros 0,5 s, antes de que el espectador llegue a leer el texto
completo o a procesar el audio — el texto confirma lo que la imagen ya contaba. Además, el
episodio tiene que poder reproducirse en bucle sin que se note el corte entre el cierre y el
siguiente visionado: el último fotograma (cierre/moraleja) debe volver a la misma pose, plano
o elemento visual del gancho (campo "bucle_visual" del esquema), para que quien lo ve una vez
no se canse al verlo dos o tres veces seguidas — eso es lo que más sube el tiempo visto medio
(objetivo > 60 % de la duración, aprendizajes.md).

BUCLE DE RETENCIÓN (orden del dueño, 20/11: el mismo bucle de dopamina que usan los casinos
para que no puedas dejar de mirar la mesa). Cada episodio tiene que montarse sobre estos 4
pasos, no solo cumplir el recuento de escenas:
1. APUESTAS: el gancho tiene que dejar claro qué pierde Felipe o Sindy si esto sale mal.
   Sin algo en juego que duela de verdad, no hay tensión y el episodio no engancha aunque
   la forma esté bien.
2. PREGUNTA: el planteamiento y el primer golpe tienen que dejar al espectador con una duda
   activa ("¿y ahora cómo sale de esto?"), no solo informarle de la situación. Si al leerlo
   se entiende todo de golpe sin ninguna curiosidad pendiente, está mal escrito.
3. GIRO: Neo tiene que resolver con algo que sorprenda, no con el desenlace que ya se veía
   venir desde el golpe 2. Si el giro es previsible, el episodio no vale aunque pase el
   validador.
4. REENGANCHE: el cierre no puede dejar la tensión completamente en reposo. La moraleja y la
   pregunta final de la pieza son ese reenganche: dejan una curiosidad abierta (la parte 2,
   u otra pregunta) antes de que el espectador suelte del todo el episodio anterior.

Reglas duras (si no las cumples, el episodio se rechaza):
1. Gancho en pantalla desde el fotograma 0, máximo 8 palabras, una situación reconocible
   (no una explicación) que deje clara la apuesta (paso 1 del bucle). Debe leerse y
   entenderse sin sonido.
2. Escalada de exactamente 3 golpes, cada uno con MÁS lógica y PEOR consecuencia que el
   anterior, manteniendo viva la pregunta del paso 2 del bucle; nunca una frase suelta sin
   relación con el golpe de antes; y nunca una frase que suene a declaración de postura o
   argumento razonado (ver AVISO DE CALIDAD arriba): cada golpe es algo que se dice en
   caliente, con ironía o sarcasmo, no un alegato.
3. El giro lo resuelve Neo y responde exactamente al conflicto planteado, no a otro, con un
   desenlace que sorprenda (paso 3 del bucle: nunca el final más obvio); deja a Rosa en
   evidencia sin alterarse. La frase de Neo también debe sonar hablada, no un comunicado:
   evita el patrón repetitivo "He [verbo] el/la [trámite]" en todos los episodios de la
   misma tanda; varía cómo lo cuenta Neo.
4. Moraleja obligatoria de 6-9 palabras, tono serio, que se entienda sola si alguien la lee
   guardada sin ver el vídeo, y que funcione como reenganche (paso 4 del bucle): no cierra
   la curiosidad del todo, apunta a la parte 2 o deja una pregunta.
5. Nunca Rosa dice la moraleja ni "Que lo resuelva el Neo" (eso lo dicen Felipe o Sindy,
   justo antes del giro, solo una vez).
6. Cifras siempre en letra, cero palabras en inglés, ningún nombre propio como primera
   palabra de una frase.
7. Prohibido: suicidio, autolesión, enfermedades o muertes reales, víctimas, política de
   partido, colectivos, marcas o empresas reales, consejos médicos/legales/financieros,
   cualquier app de Neogest Lab en el vídeo.
8. Duración implícita del conjunto de frases: episodio de 45-70 s hablado (biblia v5, orden
   del dueño 20/11 tarde: "1 al día pero de más duración"), nunca una escena de relleno.
9. Registro de habla de barrio con réplica inteligente (ver BIBLIA v5 más abajo) en Rosa,
   Felipe, Sindy y Concha Quetón; Neo siempre correcto y neutro.

NUEVO PERSONAJE (orden del dueño 20/11): "conchaqueton" (Concha Quetón, clienta morosa,
coletilla «Eso lo arreglamos la semana que viene») es una alternativa a "cliente" para dar
variedad y continuidad cuando el conflicto lo trae un cliente — úsala en el gancho/gag en vez
de "cliente" cuando encaje, nunca en el remate (eso sigue siendo solo de Neo).

BIBLIA v5 (orden del dueño, 20/11 tarde, en sus palabras): "humor negro y la ironía con
mensaje final, tiene que impactar, remover, hacer reír en plan bestia... personajes con poca
cultura al hablar pero a la vez inteligentes, que choque la diferencia, un barrio marginal,
gente de pocos recursos, estilo comedia americana... 1 episodio al día pero de más duración".
Tres cambios nuevos sobre todo lo de arriba (que sigue mandando):
1. REGISTRO DE HABLA: Rosa, Felipe, Sindy y Concha Quetón hablan en castellano popular y de
   barrio — modismos, gramática relajada, sin tecnicismos — pero lo que DICEN es agudo e
   inteligente. El choque entre cómo hablan y lo listos que son es el gancho de personalidad;
   la pobreza es el escenario (viven en un barrio humilde), nunca el chiste — el chiste va
   siempre contra el sistema o contra la propia resignación del personaje, jamás contra cómo
   habla la gente de barrio en la vida real. Neo sigue hablando correcto y neutro: ese
   contraste con el resto es parte del gag.
   MAL (registro bajo sin inteligencia, solo vulgar): "Esto es una mierda y ya está."
   BIEN (registro bajo + réplica inteligente, lo que se pide): "A mí que me paguen las horas,
   que lo de 'formar parte de la familia' ya lo cobro en cariño, y de eso no come nadie."
2. DURACIÓN Y CADENCIA: episodios de 45-70 s hablados (no 15-25 s), con espacio para que los
   3 golpes de la escalada respiren un poco más que antes; 1 episodio NUEVO al día (no varios
   cortos). Usa entre 6 y 9 escenas (antes 5-7) para llenar ese tiempo sin relleno: puedes
   añadir un golpe extra a la escalada (4 en vez de 3) si el conflicto lo pide, pero el remate
   y el cierre siguen siendo solo de Neo.
3. RECUERDO/CONTINUIDAD (orden del dueño: "llevar un orden de recuerdo en los personajes por
   situaciones anteriores"): si alguno de los temas ya usados ({temas}) encaja de forma
   natural, añade una línea breve en el cierre donde un personaje lo menciona o reacciona a
   ello (p. ej. Sindy: "Como lo del jueves, pero peor"). Si no encaja ninguno todavía, deja el
   campo "recuerdo" en null — nunca inventes una referencia a un episodio que no existe.
El plano de casa de apertura y cierre (el "estilo comedia americana" con el mismo encuadre
para el bucle) lo añade el código a partir del campo "set"/"flow" del episodio, no hace falta
escribirlo como escena.

Devuelve SOLO un array JSON (sin texto fuera del JSON, sin ``` ) con {n} objetos, cada uno
con este esquema exacto (valores de ejemplo, escríbelos tú con contenido real distinto en
cada guion; "h" solo puede ser rosa, felipe, sindy, neo, cliente o conchaqueton; "e" solo puede ser
gancho, gag, remate o cierre; usa entre 6 y 9 escenas, con el patrón gancho, 3-4x gag,
remate, cierre):
{json.dumps(esquema, ensure_ascii=False, indent=2)}
"""


def _llamar_un_modelo(modelo, api_key, body):
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
        f"?key={api_key}"
    )
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _llamar_gemini(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY no está en el entorno: no se puede pedir guiones a Gemini.")
        return None
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.9,
            "responseMimeType": "application/json",
        },
    }

    data = None
    for modelo in MODELOS:
        # "Alta demanda" (503) suele ser cosa de segundos: 2 intentos cortos con espera antes
        # de pasar al siguiente modelo de la lista, en vez de darlo por perdido a la primera.
        for intento in range(2):
            try:
                data = _llamar_un_modelo(modelo, api_key, body)
                print(f"Modelo usado: {modelo}")
                break
            except urllib.error.HTTPError as e:
                detalle = e.read().decode("utf-8", "ignore")[:300]
                print(f"{modelo} (intento {intento + 1}) -> HTTP {e.code}: {detalle}")
                if e.code == 503 and intento == 0:
                    time.sleep(8)
                    continue
                if e.code in (404, 503, 429):
                    break  # retirado/renombrado o sigue saturado/límite: probar el siguiente modelo
                return None  # otro error (clave inválida, prompt rechazado...) no se arregla cambiando de modelo
            except Exception as e:  # red, timeout...
                print(f"{modelo} (intento {intento + 1}) -> fallo de red: {e}")
                if intento == 0:
                    time.sleep(5)
                    continue
                break
        if data is not None:
            break

    if data is None:
        print(f"Ningún modelo de {MODELOS} respondió.")
        return None

    try:
        texto = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        print(f"Respuesta de Gemini sin el formato esperado: {json.dumps(data)[:500]}")
        return None

    texto = re.sub(r"^```(json)?|```$", "", texto.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(texto)
    except json.JSONDecodeError as e:
        print(f"Gemini no devolvió JSON válido: {e}\n{texto[:500]}")
        return None


def _validar(ep):
    """Rechazo mecánico de lo que ya sabemos que Calidad tumba; no sustituye su revisión."""
    motivos = []
    if not isinstance(ep.get("slug"), str) or not ep["slug"].strip():
        motivos.append("sin slug")
    if ep.get("set") not in {"oficina", "despacho", "bar", "calle", "reunion"}:
        motivos.append(f"set inválido: {ep.get('set')!r}")
    moraleja_palabras = len(str(ep.get("moraleja", "")).split())
    if not (6 <= moraleja_palabras <= 9):
        motivos.append(f"moraleja con {moraleja_palabras} palabras (debe ser 6-9)")
    if not isinstance(ep.get("bucle_visual"), str) or not ep["bucle_visual"].strip():
        motivos.append("falta bucle_visual (qué elemento del gancho se repite en el cierre para que se vea en bucle sin notar el corte)")
    escenas = ep.get("escenas") or []
    if len(escenas) < 5:
        motivos.append(f"solo {len(escenas)} escenas (mínimo 5: gancho + 3 golpes + remate)")
    estilos = [e.get("e") for e in escenas]
    if estilos[:1] != ["gancho"]:
        motivos.append("la primera escena no es el gancho")
    if "remate" not in estilos:
        motivos.append("falta el remate (giro de Neo)")
    gags = [e for e in escenas if e.get("e") == "gag"]
    if len(gags) != 3:
        motivos.append(f"{len(gags)} golpes de escalada (deben ser exactamente 3)")
    for i, g in enumerate(gags, 1):
        texto = str(g.get("t", ""))
        if PATRON_ARGUMENTO.search(texto):
            motivos.append(f"gag {i} suena a declaración de postura, no a frase hablada: {texto!r}")
        if len(texto.split()) > MAX_PALABRAS_GAG:
            motivos.append(f"gag {i} tiene {len(texto.split())} palabras (máx {MAX_PALABRAS_GAG}; si es tan largo, probablemente es un argumento, no un golpe)")
    if escenas and escenas[0].get("h") and len(str(escenas[0].get("t", "")).split()) > 8:
        motivos.append("el gancho supera las 8 palabras")
    for e in escenas:
        if e.get("e") not in ESTILOS_VALIDOS:
            motivos.append(f"estilo de escena inválido: {e.get('e')!r}")
        if e.get("h") and e["h"] not in PERSONAJES_VALIDOS:
            motivos.append(f"personaje inválido: {e['h']!r}")
    remate = next((e for e in escenas if e.get("e") == "remate"), None)
    if remate and remate.get("h") != "neo":
        motivos.append("el remate no lo dice Neo")
    return motivos


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else N_POR_DEFECTO
    os.makedirs(PENDIENTES, exist_ok=True)

    guiones = _llamar_gemini(_prompt(n))
    hoy = datetime.date.today().isoformat()

    if guiones is None:
        linea = f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M} UTC · Guionista Gemini · no se ha podido pedir guiones (ver log del workflow) · el Creador escribe el suyo como hasta ahora"
        with open(TABLON, "a", encoding="utf-8") as f:
            f.write(linea + "\n")
        print(linea)
        return 0  # no bloquea: es un paso opcional, el Creador sigue sin él

    if not isinstance(guiones, list):
        guiones = [guiones]

    guardados, rechazados = [], []
    for i, ep in enumerate(guiones):
        if not isinstance(ep, dict):
            rechazados.append((f"#{i}", ["no es un objeto JSON"]))
            continue
        motivos = _validar(ep)
        if motivos:
            rechazados.append((ep.get("slug", f"#{i}"), motivos))
            continue
        slug = re.sub(r"[^a-z0-9_]+", "_", str(ep["slug"]).lower()).strip("_") or f"ep{i}"
        nombre = f"{hoy}_{slug}.json"
        ruta = os.path.join(PENDIENTES, nombre)
        ep["fuente"] = "gemini"
        ep["generado"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(ep, f, ensure_ascii=False, indent=2)
        guardados.append(nombre)

    resumen = f"{len(guardados)} guardados, {len(rechazados)} rechazados por el validador"
    if rechazados:
        detalle = "; ".join(f"{slug}: {', '.join(m)}" for slug, m in rechazados[:3])
        resumen += f" ({detalle})"
    linea = (
        f"{datetime.datetime.now(datetime.timezone.utc):%Y-%m-%d %H:%M} UTC · Guionista Gemini · pedidos {n} "
        f"guiones para El Jambo · {resumen} · pendientes en equipo/guiones_gemini/pendientes/"
    )
    with open(TABLON, "a", encoding="utf-8") as f:
        f.write(linea + "\n")
    print(linea)
    return 0


if __name__ == "__main__":
    sys.exit(main())
