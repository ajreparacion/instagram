# Lo que solo puede hacer el dueño de la cuenta

Reducido el 13/11/2026 por el Estratega (la versión larga está en git). Aquí solo queda lo que necesita tu identidad, tus datos o el móvil; el equipo hace todo lo demás.

## Tres acciones prioritarias (por orden de efecto)
1. **Reconectar Buzzfy con permiso de mensajes** (buzzfy.co/connect/instagram?feature=messaging). Sin él no se pueden contar ni responder los DMs con intención, y hoy es la única señal de interés que no se mide.
2. **En /panel/solicitudes, marcar la solicitud del 8/11** como contactada o descartada (o decir que fue una prueba) **y decir si alguna app tiene plan de pago o precio**. Sin eso el embudo no puede medir euros.
3. **Archivar desde el móvil los duplicados** (la API no archiva): carruseles del 8/11 «Deja de pedirle así las cosas a la IA» ×3, «¿Pasas los presupuestos al Excel por la noche?» ×3, «5 tareas pesadas…» ×2 y el reel de AJ Web del 10/11 ×2; dejar uno de cada. Quitar de paso lo que aún diga «Escríbeme IDEA».

## TikTok (16/11/2026): 3 pasos tuyos, unos 15 minutos; después todo es automático
1. **Crear la cuenta** en https://www.tiktok.com/signup con el correo de la empresa. Usuario `neogestlab`, nombre «Neogest Lab». Luego, en el móvil: Perfil → menú ☰ → Ajustes y privacidad → Cuenta → **Cambiar a cuenta de empresa** (categoría «Software» o «Servicios de TI»). Foto, bio y enlace: copiar de equipo/tiktok/LEEME.md y del doc «Estrategia TikTok».
2. **Buffer gratis** en https://buffer.com (botón de registro, plan Free, sin tarjeta) → Channels → Connect → TikTok → autorizar @neogestlab.
3. **Clave de Buffer**: sigue la guía oficial https://support.buffer.com/en-us/articles/how-to-create-your-buffer-api-key-ShIgYVwM6j , copia la clave → pegarla como secreto `BUFFER_API_KEY` en https://github.com/ajreparacion/instagram/settings/secrets/actions/new . Ese mismo día salen programadas las 8 primeras piezas.

## Con fecha
- **Bio de Instagram** (Analista, 14/11): la bio en vivo aún dice «Comenta APP», un cierre prohibido; cámbiala por la oferta de prueba gratuita (propuesta en equipo/perfil_propuesto.md). Analista (15/11): confirmar si quitar «Comenta APP» de la bio fue voluntario.
- **Vídeos del Centro en «revision»** (Centro, 14-15/11): esperan tu visto bueno en el editor del Centro (VideoMezcla); sin él no salen.
- **Nombre visible** «Neogest Lab · Apps a medida»: Instagram lo bloquea hasta ~25/11 (hay recordatorio). Es lo único que falta del perfil.
- **Token de Meta:** el 12/11 a las 21:10 caducó (código 190) y volvió a funcionar a las 21:39. Si se repite, renovarlo; el equipo anotará aquí la hora.

## Decisiones tuyas (cuando puedas, no bloquean nada)
- Medios de pago en las piezas de Gestión Integral 7D: ¿nombrar Stripe, Redsys y Bizum o decir «tarjeta», «TPV» y «transferencia»? Mientras no digas nada va en genérico.
- Cuándo quieres apps en los episodios (hoy el pivote de app va en 1 de cada 3 por la fórmula v9).
- Tu vídeo de referencia (reel DfXjcjiNW8k): no se puede abrir desde el equipo; súbelo como vídeo o cuéntalo en 3 frases.
- Fijar el comentario del reel y elegir el inicio de la canción de Instagram: la API no lo permite; si no quieres hacerlo a mano, se prueba el comentario como respuesta automática.
- Facebook: confirmar qué se publica en la página (hoy sale lo mismo que en Instagram) y, desde una cuenta que no sea administradora, que se ve una pieza.
- Buzzfy: el plan actual da ~10 búsquedas al día y el Cazador lo agota; ampliar el plan (p. ej. 100/día) es decisión tuya porque tiene coste (Cazador, 15/11).
- Precios: la auditoría del Centro (14/11) ve un plan de 19 €/usuario/mes en Gestión Integral 7D; ¿se puede decir en los posts? Hasta que lo digas, no se publican precios.
- Afiliados de Amazon.es y panel de Monetización de Instagram (anotar herramientas disponibles): solo si quieres abrir esas vías; hoy no hay umbrales cumplidos.

## Hecho (no hace falta nada)
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
