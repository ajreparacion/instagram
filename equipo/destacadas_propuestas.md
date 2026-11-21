# Propuesta de historias destacadas y publicaciones fijadas

Orden del dueño (21/11/2026 madrugada): «en los perfiles añade nuestros productos, en instagram por ejemplo con historias destacadas, fijamos las publicaciones de nuestros productos, etc.»

Ningún conector puede editar esto (ni Buzzfy ni la API de Meta Business tienen una acción de "crear destacada" o "fijar publicación" de perfil): hay que hacerlo a mano en la app/web de Instagram, o por Comunidad vía Claude in Chrome/computer use cuando el ordenador del dueño esté disponible. Esta nota deja el trabajo listo para "pegar y guardar".

## Instagram (@neogestlab)

### Historias destacadas propuestas (una por producto prioritario, catálogo en `claude/contexto-neogest-lab.md`)
1. **Gestión Integral 7D** — portada: captura del dashboard principal, fondo paleta Neogest (#13305A). Contenido: 3-4 historias con capturas reales de la app + texto «Prueba gratis, sin tarjeta».
2. **GH PLUS · Gestión Hogar** — portada: icono de la app. Contenido: capturas desde la cuenta de pruebas (NUNCA la cuenta real, por datos financieros sensibles) mostrando el control de gastos del hogar.
3. **MEDICATOR** — portada: icono de la app. Contenido: función real de recordatorio de medicación.
4. **AjReparacion Gestión** — portada: icono de la app. Contenido: SOLO desde **AJ Sistema DEMO** (id 6ae702b32d473b8561ad5afb), nunca la original (datos reales del taller).
5. **El Jambo que sabe** — portada: fotograma de un episodio. Contenido: mejores momentos de la serie (engancha para volver al perfil).
6. **Centro de Contenido Apps** — portada: logo del Centro. Contenido: qué es y para qué sirve (enlaza todas las apps).

Orden sugerido en el perfil: Gestión Integral 7D primero (es la métrica que manda: altas en prueba gratuita), luego El Jambo (es lo que trae tráfico), después el resto.

### Publicaciones a fijar (3, máximo de Instagram)
1. El mejor reel de Gestión Integral 7D (más alcance o más claro sobre la función estrella).
2. El piloto de «El Jambo que sabe» v3 (en cuanto el dueño dé el visto bueno y se publique) — es el contenido más viral.
3. Un reel resumen/portada del catálogo completo de apps (Centro de Contenido Apps), para quien llega nuevo al perfil.

### Bio sugerida (coherente con `equipo/perfil_propuesto.md` del 20/11, pendiente de pegar también)
Ya redactada en `equipo/perfil_propuesto.md`. Revisar que sigue vigente (reparto de El Jambo, catchphrase «Que lo resuelva el Neo») antes de pegarla.

## Facebook / YouTube — HECHO (21/11/2026, pasada con Chrome)

### YouTube (NeogestLab) — 4 de 4 productos con Short propio, completados
Pestaña Inicio → sección por producto (tipo «Una lista de reproducción»), publicada:
- ✅ **Gestión Integral 7D**
- ✅ **MEDICATOR** (2 Shorts)
- ✅ **GPS Andaluz**
- ✅ **Factura7D Verifactu**

Resto del catálogo (GH PLUS, AJ Sistema DEMO, Insultator, Expedientes Imposibles, Centro de Contenido Apps, Gestoría7D, APPCC Fácil...) revisado por título en el canal: **no tienen Short propio todavía**. En cuanto Creador/Remasterizador generen uno, repetir el mismo patrón (crear lista → añadir el Short → sección en Pestaña Inicio).

### Facebook (Neogestlab) — corrección importante
A diferencia de Instagram, **Facebook SÍ permite fijar una publicación desde la web**, en el menú ⋯ de cada post → «Fijar publicación» (confirmado en vivo con Chrome, no hace falta API ni conector ni el móvil del dueño). Fijado ya el post de la serie morosidad/pagos a 120 días (incluye el CTA de prueba gratuita). Pendiente: sustituirlo por un post específico de Gestión Integral 7D en cuanto Comunidad publique uno que lo sea directamente (el fijado ahora es temático, no de producto).

## Estado (21/11/2026, pasada con Chrome)

### Destacadas — 3 de 6 hechas
- ✅ **Gestión 7D** — creada desde la historia «dice "te pago a 90 días"».
- ✅ **MEDICATOR** — creada desde la historia «¿Y si el móvil leyera tus recetas?».
- ✅ **Neogest Lab** (genérica) — solo quedaba 1 historia más en el archivo (un vídeo de ambiente, sin texto que la identifique con un producto concreto), así que se usó para una destacada general de marca en vez de forzarla en «El Jambo».
- ⏳ **GH PLUS, AjReparacion Gestión (DEMO), El Jambo que sabe, Centro de Contenido Apps** — bloqueadas: Instagram solo deja construir una destacada a partir de **Historias ya archivadas**, no se puede subir un vídeo nuevo directamente al crearla. No quedan historias sin usar. Para completarlas hace falta publicar antes una Historia de cada uno de esos productos (Comunidad puede encargarse en próximas pasadas) y luego convertirla en destacada.

### Publicaciones fijadas — bloqueado, es cosa del dueño (1 minuto desde el móvil)
Comprobado en vivo: **"Fijar en el perfil" no existe en Instagram para navegador/escritorio, solo en la app móvil** (confirmado también por fuentes externas). No es un fallo del agente ni de Chrome: Instagram no ofrece esa opción fuera de la app.

Pasos para el dueño, desde el móvil, app de Instagram:
1. Abrir https://www.instagram.com/p/DfwoHBzk9fg/ (reel «¿Tu cliente te paga a 90 días?», el mejor reel corto de Gestión Integral 7D) → ⋮ → **Fijar en el perfil**.
2. En cuanto el dueño apruebe y se publique el piloto de El Jambo (`cola/999_jambo_piloto_barrio`, pendiente de su visto bueno), fijarlo también → es el contenido más viral.
3. Tercera: un reel resumen del Centro de Contenido Apps (pendiente de identificar cuál, o grabar uno nuevo específico para esto).

## Siguiente paso
Cuando Comunidad publique nuevas Historias de los 4 productos pendientes, pasarlas a destacadas con este mismo procedimiento (⋯ → Nuevo contenido destacado). El fijado de publicaciones queda anotado en `equipo/pendiente_usuario.md` como tarea del dueño (no delegable a un agente, por la limitación de Instagram Web).
