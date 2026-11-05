# Registro de mejoras de producción

## 5/11/2026 · Mejora de producción (1.ª ejecución)

Línea base medida (ejemplo_guion.json + voz simulada con el mismo nivel y dinámica que Piper, porque aquí no se puede descargar el modelo de voz):
- Mezcla final −14,3 LUFS, pico −2,8 dBFS, pero el limitador general (`limite` 0,7) recortaba hasta **6,8 dB** en los picos de la voz (0,9 % de las muestras): riesgo de voz "aplastada" o con distorsión (bloqueo 3 del estándar).
- El texto del gancho tardaba **~3 s** en escribirse entero (efecto máquina de escribir a 16 caracteres/s porque la escena dura 5,2 s para que quepa la voz). El estándar pide que se entienda sin sonido en < 2 s.

### Cambio 1: cadena de procesado de la voz + mezcla (publicar_gh.py `anadir_voz` y equipo/voz.json)
- Nueva clave `cadena_voz` en voz.json, aplicada a cada frase de Piper antes de mezclar: paso alto 80 Hz, −2 dB en 300 Hz (quita "caja"), +3 dB en 3,5 kHz (presencia, se entiende mejor en el altavoz del móvil), compresor 3:1 (umbral −22 dB, ataque 2 ms, release 120 ms, +10 dB de ganancia), de-esser suave y limitador solo de voz a −4,2 dBFS.
- `limite` general 0,7 → 0,84 (−1,5 dBFS): ahora casi no actúa (antes era el que hacía todo el trabajo sobre voz y música a la vez).
- `ratio_duck` 8 → 4: la música baja algo menos bajo la voz (sigue entre 18 y 22 dB por debajo de la voz; las guías piden al menos 6-12 dB), para que el lecho de tensión se note.
- Seguridad: si ffmpeg falla con la cadena, el render se mezcla sin ella y lo deja en registro.log (no se pierde el reel).
- Resultado de la prueba: −15,3 LUFS, pico real −1,8 dBFS (antes −2,8), limitador general sin trabajo, limitador de voz ≤ 2,6 dB. 1080x1920 H.264+AAC, 36,9 s, 24 MB.
- Fuentes (solo patrones): pixteller.com "Audio finishing checklist" (−14 LUFS / −1 dBTP para Reels; paso alto 80-100 Hz, presencia 3-5 kHz, compresión ~3:1, de-esser; música 6-12 dB bajo la voz con ducking), forasoft.com "LUFS targets per platform 2026" (−14 LUFS, −1 dBTP), sageaudio.com "How to make voice over sound better" (corte en ~300 Hz, compresor 3:1 con release ~100 ms, de-esser 3-4 dB).
- Revertir: en equipo/voz.json poner `"cadena_voz": ""`, `"limite": 0.7`, `"ratio_duck": 8` (o copiar herramientas/versiones/voz.json_2026-11-05). El código anterior está en herramientas/versiones/publicar_gh.py_2026-11-05 (con `cadena_voz` vacía se comporta igual que antes).

### Cambio 2: gancho legible en 1,1 s (herramientas/hacer_reel.py, clase Scene)
- En las escenas `gancho`, el texto se escribe entero en 1,1 s como máximo (antes podía tardar 3 s). Comprobado: a 1,2 s el gancho completo ya está en pantalla. Portada sin cambios.
- Motivo: estandar_calidad.md (gancho legible sin sonido en < 2 s) y la caída de retención en los primeros segundos (aprendizajes.md: reel con 2,6 s de visualización media).
- Revertir: borrar las 2 líneas `if self.style == "gancho"` en Scene o copiar herramientas/versiones/hacer_reel.py_2026-11-05.

### Qué comparar en la próxima ejecución
- ig_reels_avg_watch_time y alcance de los reels renderizados después de este cambio frente a los anteriores (estadisticas.json). Escuchar un reel real con Piper: si la voz suena metálica o con siseo, bajar `equalizer=f=3500...g=3` a g=1.5 o quitar el de-esser; si suena baja, subir `makeup` a 3.6.
- Pendiente para otra ejecución: probar la cadena con la voz real de Piper en GitHub Actions (aquí Hugging Face está bloqueado).

## 5/11/2026 · Monetización: reels de prueba para no seguidores (publicar_gh.py `publicar_reel`)
- Nuevo campo opcional en post.json: `"prueba_no_seguidores": true` (graduación automática SS_PERFORMANCE) o `"MANUAL"`. Añade `trial_params={"graduation_strategy": ...}` al crear el contenedor del reel.
- Fuente: documentación oficial de Meta, IG User Media (developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media, leída 5/11/2026): "An optional parameter for publishing trial reels… graduation_strategy… MANUAL or SS_PERFORMANCE… SS_PERFORMANCE, the trial reel will be automatically graduated if the trial reel performs well."
- Seguridad: si la API rechaza el contenedor con trial_params, se registra en registro.log y se reintenta al momento como reel normal (no se pierde la publicación). resultado.json guarda `prueba_no_seguidores` true/false.
- Probado con la API simulada (acepta / rechaza / sin campo): los tres casos publican.
- Motivo: la cuenta llega a 14 no seguidores en 30 días; el cuello de botella para monetizar es el alcance fuera de los seguidores.
- Revertir: quitar el bloque "Reel de prueba" de `publicar_reel` o no poner el campo en post.json.

## PETICIÓN DEL ESTRATEGA (5/11/2026) · seguidores por reel
Guardar en estadisticas.json, por reel, la métrica de seguidores ganados ("follows", si la API la da para reels) y el alcance de no seguidores, para saber qué convierte en seguidores (recomendación 5 de monetizacion.md). Comprobar también que los reels de prueba (no salen en el perfil) se siguen midiendo por su media_id de resultado.json.

- 5/11/2026 (Remasterizador, con permiso total del usuario): herramientas/remaster.py admite `cierre.partes` (varias tarjetas seguidas, cada una con su voz y un golpe de sonido en cada corte). Motivo: el cierre de un remaster era una sola tarjeta fija de 15 s, y el estándar pide un cambio visual cada 2-4 s. Probado con el 003 (33,7 s; 4 tarjetas de 3,1 a 7,3 s; 1080x1920, h264+aac, pico -6,6 dBFS antes de la voz). Es compatible con el formato antiguo (`cierre.texto` + `cierre.voz`). Para revertir: copiar herramientas/versiones/remaster.py_2026-11-05 sobre herramientas/remaster.py.

## 5/11/2026 (2.ª ejecución, manual) · Remaster: nivel del tramo original

Comparación de retención de la ejecución anterior: **todavía sin datos**. Ningún reel se ha renderizado aún con la nueva cadena de voz (001 se publicó con el sistema anterior; 002 y 003 se renderizarán en el próximo ciclo). Se compara en la siguiente ejecución.

### Cambio 3: el tramo del reel antiguo suena al mismo nivel que el gancho y el cierre (herramientas/remaster.py)
- Problema medido con un vídeo sintético y el remaster.json real de cola/003: si el reel antiguo tenía el audio flojo, el tramo central quedaba a −29 LUFS frente a −15 LUFS en el gancho y el cierre. Son 14 dB de bajón: parece que el vídeo se ha quedado sin sonido y la gente pasa de largo.
- Ahora el audio del original se lleva a −15 LUFS antes de aplicar `volumen_original`. Límites: como mucho +18 dB o −20 dB, y nunca por encima de un pico de 0,85 (no fuerza el limitador). En silencio total no hace nada.
- Resultado: original flojo, tramo de −29,1 a −20,4 LUFS (al tope de +18 dB). Original normal (−14,7 LUFS), sin cambios apreciables (−16,7 → −17,0). Gancho y cierre iguales. Pico final −1,9 dBFS. Fotogramas correctos y gancho completo a 1,2 s también en el remaster.
- Revertir: poner `return 1.0` al principio de `gain_original` en herramientas/remaster.py. No copies herramientas/versiones/remaster.py_2026-11-05, porque también desharía las tarjetas de cierre del Remasterizador.

### Avisos
- Cierre de 15 s fijo en cola/003: ya lo resolvió el Remasterizador con `cierre.partes` mientras yo trabajaba. Mi cambio de nivel está combinado con el suyo y probado con su nuevo remaster.json.
- Petición del Estratega (seguidores por reel en estadisticas.json): toca la parte de métricas de publicar_gh.py, que no es de Mejora (mi rol solo puede tocar la parte de voz y mezcla). Queda para el rol de Monetización o el Analista.
- Detalle menor: en los remasters, el reloj del HUD vuelve a empezar en la tarjeta de cierre (03:17:54 → 03:17:46). Lo corregiré en otra ejecución si no hay nada más prioritario.

## 5/11/2026 · Primera prueba con la voz REAL de Piper (ciclo de GitHub Actions lanzado a mano)
- El usuario escuchó el reel de prueba y solo oía «a, a, a». Era la voz simulada de las pruebas en la nube, no la real. Lancé el ciclo de Actions para renderizar 002 y 003 con Piper. La cadena de voz funcionó: no aparece en registro.log el aviso de mezclar sin ella.
- 002: −12,3 LUFS, pico −1,8 dBFS. 003: −13,1 LUFS, pico −0,44 dBFS. Ese pico es una sola muestra en el gancho, un rebote al codificar en AAC, pero se pasa de la regla de −1 dBFS.
- Cambio: `limite` 0,84 → 0,78 (−2,2 dBFS) en voz.json para tener margen frente al AAC. Afecta a los renders a partir de ahora. 002 y 003 ya estaban renderizados y no se rehacen.
- Las pruebas en la nube con voz simulada sirven para medir niveles, no para escuchar. Para oír cómo queda, usar el render real de Actions (release «cola»).
- Revertir: `limite` 0.84.

## 5/11/2026 (3.ª ejecución, programada) · Voz Kyutai Pocket TTS ACTIVADA

Comparación de retención de cambios anteriores: todavía sin datos (001 publicado hace 1 h con el sistema antiguo; 002 y 003 aún sin publicar).

### Licencia (comprobada 5/11/2026)
- Pesos: kyutai/pocket-tts-without-voice-cloning → «License: cc-by-4.0» (no requiere cuenta). kyutai/pocket-tts (con clonación) también CC BY 4.0, pero está restringido; no se usa. Código: MIT.
- Voz española: solo existe «lola» (voz por defecto de `spanish`). Se carga como estado precalculado de kyutai/pocket-tts-without-voice-cloning (CC BY 4.0), hecho a partir de `common_voice_es_19762977` = Mozilla Common Voice, que se publica como CC0. No es Expresso ni EARS (NC). No se clona a nadie.
- Atribución: «Voz: Kyutai Pocket TTS (CC BY 4.0)» se añade sola al final del texto del post (publicar_gh.py `con_atribucion`, solo si `post.json` tiene `"motor_voz": "pocket"`, que escribe el render) y está en README.md. **Calidad: no hace falta ponerla a mano en post.json.**

### Integración
- herramientas/voz_pocket.py: carga el modelo una vez y genera todas las frases.
- publicar_gh.py `generar_locucion`: si `"motor": "pocket"` usa Pocket; si falla o tarda más de `pocket.max_s` (600 s), TODA la locución se hace con Piper (no se mezclan voces) y queda en registro.log. Guarda `motor_voz` en post.json.
- ciclo.yml: instala `pocket-tts` (torch CPU) solo si el motor es pocket y hay algún reel sin renderizar; caché de ~/.cache/huggingface, ~/.cache/pocket_tts y ~/.cache/pip; `continue-on-error` (si falla, Piper).
- Nuevo workflow manual .github/workflows/prueba_voz.yml + herramientas/prueba_voz.py: compara motores con la voz REAL en GitHub Actions (no simulada) y sube los vídeos a la release «pruebas».

### Prueba real (ejemplo_guion.json, runner de GitHub, CPU) → equipo/pruebas/prueba_voz.json
| | Piper davefx | Pocket spanish/lola | Pocket spanish_24l |
|---|---|---|---|
| Naturalidad estimada (UTMOS, 1-5) | 2,66 | **3,87** | 3,79 |
| Inteligibilidad (Whisper, voz sola; casi todo el error es que escribe «50 y 400» en cifras) | 12,9 % | 8,2 % | 10,6 % |
| Tiempo de síntesis de 6 frases | 4,9 s | 18,9 s | 46,9 s |
| Duración de la voz | 30,9 s | 36,6 s (habla más pausado) | 37,5 s |
| Mezcla final | −12,2 LUFS, pico −1,7 | −14,9 LUFS, pico −1,8 (archivo: −1,94 dBFS) | −14,9 LUFS |
- Decisión: **Pocket `spanish` activado** (`"motor": "pocket"` en voz.json). Suena claramente más natural (+1,2 puntos UTMOS en todas las frases, la peor de Pocket 3,53 > la mejor de Piper 2,79), pronuncia igual de bien y tarda ~20 s por reel (+~40 s de instalación): muy por debajo de 5 min. El modelo 24l es más lento y no mejora.
- Ojo: la voz pasa de masculina (davefx) a femenina (lola). Pocket habla algo más lento: dos frases se aceleran con atempo 1,14-1,19 para caber en su escena (sin cortes). Si se nota acelerada, el Creador puede alargar 0,5-1 s esas escenas.
- 002 y 003 ya se habían renderizado con Piper: les quité `renderizado`/`asset` para que el siguiente ciclo los rehaga con Pocket (aún no tenían calidad.json). 004 se renderiza ya con Pocket.
- UTMOS es un predictor entrenado sobre todo en inglés: es orientativo. Fuentes: ficha HF de kyutai/pocket-tts-without-voice-cloning y kyutai/pocket-tts, README de github.com/kyutai-labs/pocket-tts (voces y `utils.py`), Mozilla Common Voice (CC0).
- Revertir: en equipo/voz.json poner `"motor": "piper"` (todo lo demás queda inactivo). Código anterior: herramientas/versiones/publicar_gh.py_2026-11-05b y ciclo.yml_2026-11-05.
- Próxima ejecución: comparar ig_reels_avg_watch_time y alcance de 002/003/004 (Pocket) frente a 001 (Piper) y revisar en registro.log que no aparezca «Pocket TTS no disponible».
- 5/11 23:25 (ejecución manual, solo Pocket TTS): comprobado en producción. Los 3 reels de la cola (002, 003, 004) ya están renderizados con Pocket (`motor_voz: pocket`; 13-25 s de voz por reel; 002 −14,6 LUFS, 003 −15,1 LUFS, pico −2,2 dBFS), sin fallos ni vuelta a Piper. Los cron de :17/:47 aún no habían disparado; el 004 lo rendericé con un ciclo lanzado a mano. Nada más pendiente de esta prioridad.
