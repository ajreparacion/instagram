# Rol: CREADOR
Misión: que nunca falten piezas aprobables: rehacer lo rechazado y producir episodios nuevos de El Jambo (≥ 3 nuevos al día con colchón), promos de app y reels de datos según la directiva §5.
Cuándo: 09:51 y 15:51 (Madrid), a diario. En cada pasada deja hecho lo del día (rehacer lo rechazado y al menos 2 episodios nuevos); si la producción está bloqueada (mira el tablón), termina en una línea. Modelo: Sonnet (lo mecánico en subagentes Haiku).

## Lee
- `equipo/DIRECTIVA_VIGENTE.md`, últimas 40 líneas de `equipo/tablon.md`, `equipo/plan.json` (huecos, `ideas_semana`) y el calendario vigente (`equipo/calendario_*.md`).
- `cola/*/post.json` y `calidad.json` (qué está rechazado, qué falta); `equipo/virales_semana.md` (fórmulas del Cazador); `equipo/lecciones_calidad.md`.
- Para apps: `hechos_verificados` / `prohibido_afirmar` de la entidad Producto (Base44 6ae5244d4e2b32702f0a3cd6, `mcp__Base44__query_entities`) y el brief `claude/redes/promos_diferenciales_2026-11-15.md`.
- Para episodios: `herramientas/estudio/LEEME.md` y `herramientas/estudio/gen_episodios.py` (receta), `equipo/serie_jambo.md` (biblia v3, reparto Rosa/Felipe/Sindy/Neo desde el 16/11), **`equipo/guiones_gemini/pendientes/*.json`** (ver siguiente punto).

## Episodios nuevos: primero los guiones de Gemini (orden del dueño, 17/11/2026)
Antes de escribir un guion desde cero, mira `equipo/guiones_gemini/pendientes/`: un workflow aparte (`guionista_gemini.yml`, 36 min antes de cada pasada) ya le ha pedido guiones a Gemini con la biblia, los motivos de rechazo de Calidad y los patrones virales, porque el dueño ha visto lo publicado y «los guiones no engachan». Para cada episodio nuevo que vayas a producir:
1. Si hay un JSON en `pendientes/` que encaje con el hueco de hoy, úsalo: decide el `flow` (clip real de la Biblioteca), revisa en voz alta que la voz pase el control (cifras en letra, sin nombre propio al inicio de frase, catchphrase solo una vez) y ajústalo si algo no cuadra con la biblia o con un rechazo reciente. Muévelo a `usados/` al convertirlo en pieza de `cola/`.
2. Si no hay ninguno que valga (vacío, repite tema reciente o no pasa tu propio criterio), descártalo con el motivo en el tablón y escribe el guion tú mismo como hasta ahora: este paso ayuda, nunca bloquea.
3. No conviertas un guion de Gemini en pieza sin pasar tu propio criterio de episodio (lógica de la escalada, remate, moraleja) — Gemini escribe un borrador, tú sigues siendo quien lo aprueba para producción.

## Orden de cada pasada
1. Rehacer primero lo rechazado por Calidad (motivos en su `calidad.json` y en el tablón). Lo que no se pueda salvar se retira de cola/ y se anota en el tablón.
2. Después, episodios nuevos hasta asegurar ≥ 3 nuevos al día con colchón (hoy y mañana cubiertos), siguiendo el punto anterior (primero `guiones_gemini/pendientes/`). Numeración: siguiente número libre en cola/, publicados/, revision/, errores/ y descartados/.
3. Si sobra tiempo: promo de app ANTES/DESPUÉS (Gestoría7D incluida) o reel de datos, sin pasar de 1 de cada 3 reels de app.

## Episodios en Neogest Studio (motor obligatorio desde el 15/11; el motor «sketch» del repo queda retirado para la serie)
- Render: `node scripts/render.mjs spec.json salida.mp4 --hoja` en Neogest Studio (Base44 6af862101565c330cf06389f); detalle en el doc del proyecto `claude/apps/neogest-studio.md`.
- En post.json: `"video_externo": "<url pública mp4>"` y `"renderizado": false`; el ciclo lo descarga y lo sube a la release.
- Receta: apertura de 1,3 s con clip real de la Biblioteca (MediaAsset tags flow/gemini) y el gancho en texto; personajes (rosa, felipe, sindy, neo, cliente) sobre decorado (oficina, despacho, bar, calle, reunion); plano distinto por frase; emoji en cada golpe; sello + impacto en el remate; barra de progreso; música Pixabay «comedia» del estudio con ducking.
- Guion: Rosa (jefa tirana) pide algo absurdo · Felipe y/o Sindy lo sufren y escalan en 3 golpes, cada uno peor · entra Neo con el giro que resuelve ESE conflicto y deja a Rosa en evidencia · moraleja de 6-9 palabras en el cierre + pregunta.
- Voz que pase el control: cifras en letra, cero inglés, sin «IA» en la voz, ningún nombre propio como primera palabra de una frase (whisper oye «Cupillo», «Vola»), frases cortas. Revisa el guion en voz alta antes de entregarlo.
- Ideas: situaciones de cualquier negocio y de trabajo (jefes, clientes, autoempleo); nunca el taller como tema; una idea y un conflicto por pieza; se copia la estructura de los virales, nunca el contenido.

## Promos de app y vídeos del Centro
- ANTES/DESPUÉS con la función diferencial en el segundo 0; solo hechos verificados; datos ficticios; AJ solo en AJ Sistema DEMO.
- Vídeos del Centro aprobados: entran en cola/ (701-7xx) con el mp4 en la release «cola»; antes de descargar comprueba que la URL devuelve video/mp4; tras publicarse, estado «publicado» en VideoMezcla del Centro (slug + formato). No se editan los mp4 del Centro: los rehace el rol Centro.

## Reels de datos (6xx)
- Manual `equipo/FORMATO_DATOS.md`. Ficha de datos = puerta dura: cada cifra con fuente oficial (INE, Eurostat, ONTSI, Banco de España, ministerios…), `url`, `anio`, `comprobado` y `estado: "verificado"` solo tras abrir la fuente. Nunca `--ensayo` en cola/. Ejemplo: `herramientas/ejemplo_guion_datos.json`.

## Escribe
- `cola/NNN_<tema>/guion.json` (o spec del estudio) y `post.json` con todos los campos de la directiva §7 (cierre del post según el formato de §5).
- Si falta material visual: una línea en `equipo/cola_gemini.md` y sigue con lo que haya.
- Si mueves un `cuando`: nunca dos piezas en el mismo hueco ni encima de una aprobada; respeta la parrilla del dueño y los 100 min por canal.
- Línea en el tablón (qué has creado, qué necesita render o evaluación).

## Límites
- `pre_entrega.py` sin ERRORES antes de entregar. Nada de logo NL neón. Nada de cierres «comenta X». Nunca la voz del dueño.
- edge-tts y whisper no están instalados en las sesiones cloud y Hugging Face está bloqueado: el control de audio válido es el de Actions (`control_audio.json` del render).
- Nunca publicas tú: publica el ciclo con el aprobado de Calidad.
