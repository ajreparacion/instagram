# Rol: CREADOR (cada día, 9:51)
1. Lee equipo/plan.json, equipo/aprendizajes.md, equipo/estandar_calidad.md, equipo/monetizacion.md (si existe), estadisticas.json y los post.json de cola/ y publicados/ (para no repetir casos y saber el número de expediente).
2. Si ya hay 2 o más reels nuevos (sin remaster.json) pendientes en cola/, no crees otro.
3. Toma la entrada de HOY con "tipo":"nuevo" del plan (idea, gancho, hora). Si no hay, elige tú un caso real potente que no se haya publicado. Si la idea es "Parte 2 SI...", comprueba la condición en estadisticas.json.
4. Investiga con 3-6 búsquedas web y al menos 2 fuentes fiables que coincidan.
5. Escribe guion.json (5-7 escenas, 25-40 s: gancho de máx. 10 palabras, archivo, 1-2 evidencia, giro, cierre con CTA) y post.json (con palabra_clave y respuesta). Autoevalúa con el estándar; si baja de 75, reescribe.
6. Prueba el render en la nube antes de subir: pip install --break-system-packages pillow numpy si falta; python3 herramientas/hacer_reel.py cola/<NNN>/guion.json /tmp/prueba.mp4; mira 2 fotogramas con Read. No subas el vídeo (lo renderiza GitHub Actions).
7. Commit y push de cola/<NNN_tema>/ (guion.json y post.json, "cuando" hoy a la hora del plan, 20:40 por defecto; si ya pasó, mañana).
8. SendUserMessage breve: título, hora, nota de autoevaluación y fuentes.

## Reglas de monetización (desde el 5/11/2026, objetivo del usuario: monetizar)
- Cierre con CTA doble: «Comenta 'PALABRA'» + «Envíaselo a quien…», y en el texto del post «Sigue la cuenta: cada noche, un expediente nuevo».
- La palabra clave siempre sin tildes (la detección no las ignora).
- Si existe un libro o documental de referencia sobre el caso, anótalo en "_nota_creador" de post.json como candidato a enlace de afiliado. En "Fuentes:" solo va lo que se ha leído de verdad.
- Contenido válido para España y Latinoamérica (evita referencias solo locales). 1 de cada 3 expedientes, sobre animales o naturaleza.
- Puedes dejar en cola hasta 2 reels nuevos por delante (hoy y mañana), siempre que el plan tenga la entrada.
