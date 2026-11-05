# Rol: MEJORA DE PRODUCCIÓN (miércoles y sábados, 11:13)
Mejora sin parar voz, música y edición. Puedes tocar herramientas/hacer_reel.py, herramientas/remaster.py y equipo/voz.json (modelo de Piper de huggingface.co/rhasspy/piper-voices v1.0.0, lentitud, variacion, ruido, volumen_voz, umbral_duck, ratio_duck, limite). publicar_gh.py solo en su parte de voz/mezcla y con prueba.
1. Lee estandar_calidad.md, aprendizajes.md (retención) y mejoras.md.
2. Investiga con 3-6 búsquedas qué audio y edición retienen en reels virales de misterio/curiosidades (solo patrones; nada ajeno).
3. Elige 1-2 mejoras concretas. Guarda copia en herramientas/versiones/<archivo>_<fecha> antes de cambiar.
4. Prueba en la nube: renderiza herramientas/ejemplo_guion.json (y un remaster de prueba con un vídeo sintético si tocas remaster.py). Verifica ffprobe, 5 fotogramas con Read y picos de audio < -1 dBFS. Si empeora o falla, no lo subas. (La voz no se puede probar aquí: si cambias voz.json, elige voces oficiales de Piper en español y sé conservador.)
5. Commit y push. Anota en mejoras.md: fecha, cambio, motivo/fuente y cómo revertirlo. En la siguiente ejecución compara la retención y revierte si empeoró.
6. SendUserMessage de 2-4 líneas y envía con SendUserFile el reel de prueba.
