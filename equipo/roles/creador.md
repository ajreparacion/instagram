# Rol: CREADOR (cada día, 9:51)
1. Lee equipo/plan.json, equipo/aprendizajes.md, equipo/estandar_calidad.md, equipo/monetizacion.md (si existe), estadisticas.json y los post.json de cola/ y publicados/ (para no repetir casos y saber el número de expediente).
2. Si ya hay 2 o más reels nuevos (sin remaster.json) pendientes en cola/, no crees otro.
3. Toma la entrada de HOY con "tipo":"nuevo" del plan (idea, gancho, hora). Si no hay, elige tú un caso real potente que no se haya publicado. Si la idea es "Parte 2 SI...", comprueba la condición en estadisticas.json.
4. Investiga con 3-6 búsquedas web y al menos 2 fuentes fiables que coincidan.
5. Escribe guion.json (5-7 escenas, 25-40 s: gancho de máx. 10 palabras, archivo, 1-2 evidencia, giro, cierre con CTA) y post.json (con palabra_clave y respuesta). Autoevalúa con el estándar; si baja de 75, reescribe.
6. Prueba el render en la nube antes de subir: pip install --break-system-packages pillow numpy si falta; python3 herramientas/hacer_reel.py cola/<NNN>/guion.json /tmp/prueba.mp4; mira 2 fotogramas con Read. No subas el vídeo (lo renderiza GitHub Actions).
7. Commit y push de cola/<NNN_tema>/ (guion.json y post.json, "cuando" hoy a la hora del plan, 20:40 por defecto; si ya pasó, mañana).
8. SendUserMessage breve: título, hora, nota de autoevaluación y fuentes.
