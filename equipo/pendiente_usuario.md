# Lo que solo puede hacer el dueño de la cuenta

Reducido el 13/11/2026 por el Estratega (la versión larga está en git). Aquí solo queda lo que necesita tu identidad, tus datos o el móvil; el equipo hace todo lo demás.

## Tres acciones prioritarias (por orden de efecto)
1. **Reconectar Buzzfy con permiso de mensajes** (buzzfy.co/connect/instagram?feature=messaging). Sin él no se pueden contar ni responder los DMs con intención, y hoy es la única señal de interés que no se mide.
2. **En /panel/solicitudes, marcar la solicitud del 8/11** como contactada o descartada (o decir que fue una prueba) **y decir si alguna app tiene plan de pago o precio**. Sin eso el embudo no puede medir euros.
3. **Archivar desde el móvil los duplicados** (la API no archiva): carruseles del 8/11 «Deja de pedirle así las cosas a la IA» ×3, «¿Pasas los presupuestos al Excel por la noche?» ×3, «5 tareas pesadas…» ×2 y el reel de AJ Web del 10/11 ×2; dejar uno de cada. Quitar de paso lo que aún diga «Escríbeme IDEA».

## Zernio (21/11/2026): 1 paso tuyo, 2 minutos — tercera vía de TikTok, ya publica de verdad
Conectaste TikTok (@neogest.lab) e Instagram (@neogestlab) en Zernio por MCP. Falta solo la clave para que el robot (workflow automático) también pueda usarla:
1. Entra en https://zernio.com/dashboard/api-keys (misma cuenta que conectó TikTok/IG) → «Create API key» → cópiala (empieza por `sk_`, no se vuelve a mostrar).
2. Pégala como secreto `ZERNIO_API_KEY` en https://github.com/ajreparacion/instagram/settings/secrets/actions/new .
En cuanto esté el secreto, `redes_zernio.yml` empieza a programar en TikTok dos veces al día (ver `equipo/zernio/LEEME.md`), sin depender de que Buffer vuelva.

## Fijar publicaciones en el perfil (21/11/2026): solo se puede desde el móvil, 1 minuto
Comprobado: Instagram **no** deja fijar publicaciones desde el navegador/ordenador, solo desde la app del móvil (los destacados y el resto sí se hicieron ya desde Chrome). Desde tu móvil, con la app de Instagram:
1. Abre https://www.instagram.com/p/DfwoHBzk9fg/ (reel «¿Tu cliente te paga a 90 días?», el mejor reel corto de Gestión Integral 7D) → ⋮ (arriba a la derecha) → **Fijar en el perfil**.
2. Cuando apruebes y se publique el piloto de El Jambo, fíjalo también (es el más viral).
Detalle completo en `equipo/destacadas_propuestas.md`.

## Historias destacadas (21/11/2026): hechas 3 de 6, faltan 4 historias nuevas
Ya están en el perfil: **Neogest Lab**, **MEDICATOR** y **Gestión 7D**. Para las 4 que faltan (GH PLUS, AjReparacion DEMO, El Jambo, Centro de Contenido Apps) hace falta publicar antes una Historia de cada uno — Instagram solo deja crear destacadas a partir de Historias ya archivadas, no se puede subir vídeo nuevo directamente. Comunidad las irá publicando; no hace falta que hagas nada salvo si quieres subir tú alguna Historia para acelerarlo.

## Guionista Gemini (17/11/2026): 1 paso tuyo, 2 minutos; después todo es automático
Pediste automatizar que los guiones de El Jambo se pidan a Gemini porque no engachaban; ya está montado (`.github/workflows/guionista_gemini.yml` + `herramientas/guionista_gemini.py`), pero necesita una clave que solo tú puedes crear:
1. Entra en https://aistudio.google.com/app/apikey con la cuenta de Google **darbish** (la misma que usas para Flow/Gemini) y pulsa «Create API key» (capa gratis, sin tarjeta).
2. Copia la clave y pégala como secreto `GEMINI_API_KEY` en https://github.com/ajreparacion/instagram/settings/secrets/actions/new .
En cuanto esté el secreto, el workflow empieza a dejar borradores de guion en `equipo/guiones_gemini/pendientes/` antes de cada pasada del Creador (09:51 y 15:51); si tarda en llegar, lánzalo tú con «Run workflow» en la pestaña Actions del repo para probarlo antes.

## TikTok (21/11/2026): cuenta creada y conectada — solo falta que Buffer vuelva (su caída, no tuya)
Pasos 1 y 2 ya hechos (cuenta de empresa @neogestlab creada y conectada). Buffer está caído ahora mismo (caída del propio servicio, no de la cuenta): en cuanto vuelva, confirma que @neogestlab sigue apareciendo en Buffer → Channels y pega la clave de API:
- **Clave de Buffer**: https://support.buffer.com/en-us/articles/how-to-create-your-buffer-api-key-ShIgYVwM6j , copia la clave → pégala como secreto `BUFFER_API_KEY` en https://github.com/ajreparacion/instagram/settings/secrets/actions/new . Ese mismo día salen programadas las 8 primeras piezas.
- Mientras Buffer esté caído, hay dos vías de reserva que no dependen de él: **Zernio** (ver sección propia arriba, publica de verdad) y **Metricool** (`redes_metricool.yml`, solo deja los posts en BORRADOR hasta confirmar los campos exactos que pide TikTok) — los 3 secretos son `METRICOOL_TOKEN`, `METRICOOL_USER_ID`, `METRICOOL_BLOG_ID`, según `equipo/metricool/LEEME.md`.

## Recepcionista 24h (16/11/2026): grabar 3 llamadas reales con el móvil, unos 5 minutos
Llama desde el móvil al número directo del asistente (contesta al momento; el fijo de la web tarda 5 tonos y en horario de taller puede cogerlo una persona), pon el altavoz y graba el sonido (grabadora de voz o grabación de pantalla con micrófono). Una pregunta por llamada: (1) «¿Qué horario tenéis?» · (2) «Quería pedir cita para esta semana» · (3) «¿Me puedes pasar con una persona?». Sin dar nombres ni teléfonos de nadie. Sube los 3 vídeos a la Biblioteca de Neogest Studio o adjúntalos en el chat.

## LinkedIn y Google (16/11/2026): cuando tengas el portátil; la clave de Buffer es la misma de TikTok
1. **LinkedIn:** con tu perfil personal abierto, crea la página en https://www.linkedin.com/company/setup/new/ → «Empresa» → nombre «Neogest Lab», URL `neogestlab`, sector «Desarrollo de software», tamaño 1-10. Logo y textos: doc «Estrategia LinkedIn y Google». Luego en Buffer: Channels → Connect → LinkedIn → elegir la **página** (no tu perfil).
2. **Google:** crea la ficha en https://business.google.com/create → nombre «Neogest Lab», categoría «Empresa de software», sin tienda física (zona de servicio: España), web y teléfono. **Verifícala** como te pida Google (suele ser un vídeo corto o un código). Cuando salga «Verificada», en Buffer: Channels → Connect → Google Business Profile.
No hay que tocar GitHub: en la siguiente pasada (07:23 o 16:23) el sistema detecta cada canal nuevo y empieza a programar.

## Con fecha
- **Bio de Instagram** (Analista, 14/11): la bio en vivo aún dice «Comenta APP», un cierre prohibido; cámbiala por la oferta de prueba gratuita (propuesta en equipo/perfil_propuesto.md). Analista (15/11): confirmar si quitar «Comenta APP» de la bio fue voluntario.
- **Vídeos del Centro en «revision»** (Centro, 14-15/11): esperan tu visto bueno en el editor del Centro (VideoMezcla); sin él no salen.
- **Nombre visible** «Neogest Lab · Apps a medida»: Instagram lo bloquea hasta ~25/11 (hay recordatorio). Es lo único que falta del perfil.
- **Token de Meta:** el 12/11 a las 21:10 caducó (código 190) y volvió a funcionar a las 21:39. Si se repite, renovarlo; el equipo anotará aquí la hora.

## Decisiones tuyas (cuando puedas, no bloquean nada)
- Medios de pago en las piezas de Gestión Integral 7D: ¿nombrar Stripe, Redsys y Bizum o decir «tarjeta», «TPV» y «transferencia»? Mientras no digas nada va en genérico.
- Tu vídeo de referencia (reel DfXjcjiNW8k): no se puede abrir desde el equipo; súbelo como vídeo o cuéntalo en 3 frases.
- Fijar el comentario del reel y elegir el inicio de la canción de Instagram: la API no lo permite; si no quieres hacerlo a mano, se prueba el comentario como respuesta automática.
- Facebook: confirmar qué se publica en la página (hoy sale lo mismo que en Instagram) y, desde una cuenta que no sea administradora, que se ve una pieza.
- Buzzfy: el plan actual da ~10 búsquedas al día y el Cazador lo agota; ampliar el plan (p. ej. 100/día) es decisión tuya porque tiene coste (Cazador, 15/11).
- Precios: la auditoría del Centro (14/11) ve un plan de 19 €/usuario/mes en Gestión Integral 7D; ¿se puede decir en los posts? Hasta que lo digas, no se publican precios.
- Afiliados de Amazon.es y panel de Monetización de Instagram (anotar herramientas disponibles): solo si quieres abrir esas vías; hoy no hay umbrales cumplidos.

## Hecho (no hace falta nada)
- Cadencia y mezcla de contenidos (orden del dueño, 19/11): resuelta; 2 reels al día, 70 % de presupuestos y facturas para autónomos y pymes y 30 % trucos de IA. No requiere otra acción del dueño.
- Bio nueva y enlace /solicitar?src=instagram (verificado con Buzzfy 11/11); categoría puesta (dicho por el dueño); usuario @neogestlab.
- Voz del dueño retirada: voz genérica de España (9/11). Voz clonada y prototipos 017-024: ya no dependen de validar θ/seseo.
- Token PAGE_TOKEN renovado (8/11); ice breakers del chat configuradas y verificadas (7/11); repositorio público y reels por release.
- Facebook: app de Meta, token de página y secreto FACEBOOK_PAGE_TOKEN creados (12/11); registro.log del 13/11 ya muestra publicaciones en Facebook.
- YouTube: canal NeogestLab con publicación de Shorts por OAuth (registro.log del 13/11 muestra Shorts publicados).
- Studio Beats PRO: licencia de muestras confirmada (11/11). Proxy de sesiones ya deja entrar a *.base44.app (11/11).
- Anulados: Matías y sus nombres, tema taller, material de anécdotas del taller, «Escríbeme IDEA» como cierre.

## Pendiente del equipo (no del dueño; se deja aquí para no perderlo)
- Modo `/demo` público (datos de ejemplo, que guarde en memoria de la pestaña) en GH PLUS, MEDICATOR, Studio Beats PRO y Gestión Integral 7D para grabar las novedades con la app real: Mejora, con el MCP de Base44 si la sesión lo tiene.
- Editor del canal: destacadas y fijados del perfil necesitan una sesión con Chrome (la tarea en la nube no lo tiene); no es una acción tuya salvo que actives «Requerir este ordenador».
- YouTube: responder comentarios exige el alcance youtube.force-ssl en el token de refresco; si falta, quedan en comunidad/sin_publicar.json (lo revisa Comunidad).

## Ventas · Prospección: red de la sesión (14/11/2026)
La tarea no puede leer workana.com ni ajreparacion.com (ENOTFOUND: fuera de los dominios permitidos de la sesión) y WebSearch (solo EE. UU.) no da anuncios fechados. Para que haya propuestas y maquetas: permitir en la red del entorno workana.com, malt.es, freelancer.es, fiverr.com, ajreparacion.com y los directorios públicos de empresas (paginasamarillas.es, einforma.com); o que el dueño pegue 3-5 enlaces de anuncios y 3 negocios de Palma.

## Requiere PC
- 14/11/2026: por orden del dueño nada se ejecuta en su ordenador. Los agentes anotan aquí lo que solo se pueda hacer en él (no se hace solo).

## Facebook · invitaciones
- 2026-11-16 · Comunidad: sin lista de candidatos para invitar (no hay en el repo a quién invitar hoy; la API no permite invitar). Si quieres invitar, usa el botón «Invitar» de la página con quienes ya comentan o reaccionan en los reels de Neogest Lab.
- 2026-11-16 · Calidad · Subir vídeos corregidos a la release «cola»: desde las sesiones en la nube no se puede (subida binaria bloqueada) y el sandbox del estudio da 401. 308 y 323 tienen el máster corregido en Neogest Studio (public/_render/fix-308.mp4 y fix-323.mp4) pero no pueden publicarse. Hace falta que Mejora habilite una vía en Actions (p. ej. que el ciclo descargue un video_externo con URL pública de media.base44.com) o que el dueño dé permiso de subida.
