# Rol: MEJORA DE PRODUCCIÓN (miércoles y sábados, 11:13)
> Desde el 6/11/2026 20:27 manda la DIRECTIVA VIGENTE de INSTRUCCIONES_EQUIPO.md (IA fácil, modo dibujo con Bit y Paco). Prioridad 1: "modo":"dibujo" en hacer_reel.py (petición en mejoras.md). Lo de abajo sobre humanizar, fotos o vídeo real queda en desuso.

Mejora sin parar voz, música y edición. Puedes tocar herramientas/hacer_reel.py, herramientas/remaster.py, herramientas/voz_*.py y equipo/voz.json ("motor": chatterbox | kokoro | pocket | piper, "respaldo", ajustes de cada motor, volumen_voz, umbral_duck, ratio_duck, limite, cadena_voz, recorte). publicar_gh.py solo en su parte de voz/mezcla/render y con prueba. Licencias: solo motores con uso comercial permitido (Chatterbox MIT, Kokoro Apache 2.0, Pocket CC BY 4.0 con atribución, Piper MIT). Prohibidos F5-TTS y afinados CC-BY-NC, XTTS/Coqui (CPML), Fish Speech, OmniVoice. Nunca clones la voz de otra persona real: solo voces/referencia_usuario.wav (si el usuario la deja) o una referencia sintética con licencia libre.
1. Lee estandar_calidad.md, aprendizajes.md (retención) y mejoras.md.
2. Investiga con 3-6 búsquedas qué audio y edición retienen en reels virales de misterio/curiosidades (solo patrones; nada ajeno).
3. Elige 1-2 mejoras concretas. Guarda copia en herramientas/versiones/<archivo>_<fecha> antes de cambiar.
4. Prueba en la nube: renderiza herramientas/ejemplo_guion.json (y un remaster de prueba con un vídeo sintético si tocas remaster.py). Verifica ffprobe, 5 fotogramas con Read y picos de audio < -1 dBFS. Si empeora o falla, no lo subas. (La voz no se puede probar aquí porque Hugging Face y PyPI están bloqueados: lánzala en GitHub Actions con "Prueba de voz" (prueba_voz.yml), lee equipo/pruebas/prueba_voz.json y descarga los mp3/mp4 de la release «pruebas».)
5. Commit y push. Anota en mejoras.md: fecha, cambio, motivo/fuente y cómo revertirlo. En la siguiente ejecución compara la retención y revierte si empeoró.
6. SendUserMessage de 2-4 líneas y envía con SendUserFile el reel de prueba.

## HECHO (5/11/2026): voz Pocket TTS (sustituida el 6/11 por Chatterbox/Kokoro si la prueba lo confirma; ver mejoras.md)
Voice Studio del usuario trae Kyutai Pocket TTS (paquete pip `pocket-tts`, código MIT, pesos CC BY 4.0: uso comercial permitido con atribución; funciona en CPU y tiene español: `spanish` y `spanish_24l`, voz por defecto «lola»). OmniVoice NO se usa: sus pesos son CC BY-NC (no comercial).
1. Comprueba en la ficha de Hugging Face (kyutai/pocket-tts-without-voice-cloning y kyutai/tts-voices) la licencia de los pesos y de la voz española que elijas. Las voces de los conjuntos Expresso o EARS son NC: prohibidas. Usa solo voces CC0 o CC BY. Si no hay ninguna voz española con licencia comercial, no lo integres y anótalo en mejoras.md.
2. Integra Pocket TTS en publicar_gh.py como motor de voz opcional (equipo/voz.json: "motor": "pocket" | "piper"), con caché del modelo en el workflow (actions/cache) y Piper como respaldo si falla.
3. Prueba con herramientas/ejemplo_guion.json: compara Piper y Pocket (naturalidad, pronunciación, tiempo de generación en CPU). Activa Pocket solo si suena claramente mejor y tarda menos de 5 minutos por reel.
4. Si lo activas, añade la atribución «Voz: Kyutai Pocket TTS (CC BY 4.0)» al final del texto de cada post (en publicar_gh.py, al publicar) y en README.md.
5. Nunca clones voces de otras personas. La voz del propio usuario solo con un modelo de licencia comercial y solo si él lo pide.
