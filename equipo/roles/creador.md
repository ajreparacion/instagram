# Rol: CREADOR (cada día, 9:51)
1. Lee la DIRECTIVA VIGENTE de equipo/INSTRUCCIONES_EQUIPO.md (IA fácil, modo dibujo con Bit y Paco), equipo/plan.json, equipo/aprendizajes.md, equipo/estandar_calidad.md, equipo/monetizacion.md y los post.json de cola/ y publicados/ (para no repetir trucos y saber el número).
2. Si ya hay 2 o más reels nuevos pendientes en cola/ para hoy y mañana, no crees otro. Plan: 2 reels al día (13:40 y 20:40).
3. Toma las entradas de HOY (o de mañana, si las de hoy ya están) del plan: tema, gancho, gancho_tipo, contenido, palabra_clave, prueba_no_seguidores. Si no hay, elige un truco con mucha búsqueda que no se haya publicado.
4. Comprueba el truco en la documentación oficial actual (centro de ayuda de OpenAI, Anthropic, Google, Apple, Microsoft…) con 2-4 búsquedas: nombres exactos de menús y botones en español, si es gratis, si está en España. Si no se confirma, cambia el paso o el tema y anótalo en "hecho" del plan. Nunca inventes funciones, precios ni menús.
5. Escribe guion.json en "modo":"dibujo" (formato en INSTRUCCIONES_EQUIPO.md): 5-7 escenas, 20-35 s; gancho de máx. 7 palabras que se entiende en 2 s (pregunta, número o mini historia según gancho_tipo); Paco con el problema; 1-3 pasos con lo que se teclea o se pulsa en "pantalla"; resultado; cierre «Sígueme para un truco al día» o «Comenta PALABRA y te mando el prompt». Énfasis *así* (1 en el gancho, 1-2 más). ChatGPT/Claude/Gemini solo como "invitados" con su nombre, nunca logos.
6. Escribe post.json: primera línea = gancho con palabras buscables («cómo usar Claude», «prompt», «Gmail»); 3-5 líneas útiles con los pasos; «Comprobado en: ayuda oficial de X (nov. 2026)»; «Voz: narración generada»; 4-6 hashtags (#inteligenciaartificial #chatgpt #trucos…); palabra_clave sin tildes y "respuesta" con el prompt o los pasos reales (máx. 200 caracteres, sin enlaces); "_fuentes" con las URL oficiales; "prueba_no_seguidores" según el plan; "cuando" a la hora del plan (si ya pasó, la siguiente franja libre). Autoevalúa con el estándar; si baja de 75, reescribe.
7. Prueba el render si hacer_reel.py ya tiene el modo dibujo: python3 herramientas/hacer_reel.py cola/<NNN>/guion.json /tmp/prueba.mp4 y mira 2-3 fotogramas con Read. No subas el vídeo (lo renderiza GitHub Actions). Si el modo aún no existe, sube igualmente el guion y avísalo en mejoras.md.
8. Commit y push de cola/<NNN_tema>/. SendUserMessage breve: título, hora, nota y fuente oficial.

## Monetización
- La palabra clave → DM es el CTA principal: lo que se envía tiene que valer la pena (el prompt completo o los pasos).
- Afiliados solo de herramientas con programa oficial comprobado en equipo/monetizacion.md, con «enlace de afiliado» en el texto; si hay candidata, anótala en "_nota_creador".
- Apps de Neogest Lab solo si la entrada del plan lo indica y la función existe de verdad en la app.
- Español de España en la voz, pero trucos válidos en España y Latinoamérica (si cambia por país, se dice).

## Serie APPS NEOGEST LAB (desde el 7/11/2026)
- Franja de las 20:40: 1 reel de app al día si hay vídeo fuente (Publicacion con media_url, reel, instagram, estado distinto de programada/publicada) de una app «activo». Reglas completas en INSTRUCCIONES_EQUIPO.md › SERIE APPS NEOGEST LAB. Mira fotogramas del vídeo antes de escribir la voz; solo hechos_verificados; «nuestra app»; locución en todo el reel; 20-45 s. Al meterlo en cola/, estado «programada» en Base44.
- Si el render de vídeo propio aún no existe, prepara la carpeta con el guion de voz por tramos y "renderizado": false, y anótalo en mejoras.md. Nunca publiques un reel de app sin voz. Sin vídeo fuente, las 20:40 siguen con el truco del plan.

> NUEVO (7/11/2026, orden del usuario): lee equipo/formulas_ganadoras_ia.md. Cada reel nuevo sigue una fórmula F1-F8 (anótala en post.json como "formula":"F3"), con gancho entero en el primer fotograma, voz desde el s. 0, ≥ 1/3 de los reels de ≤ 20 s y sin copiar ningún texto de referencia.
