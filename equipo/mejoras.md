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
