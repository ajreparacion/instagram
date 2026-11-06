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

## 6/11/2026 · El ciclo de GitHub no arranca solo: respaldo
- Desde que existe, "Ciclo Instagram" nunca se ha ejecutado por su horario (`schedule`). Todas las ejecuciones han sido manuales (`workflow_dispatch`), también después de pasar el cron a los minutos 17 y 47 y de desactivar y reactivar el workflow por API. Causa probable: el archivo del workflow solo lo han guardado bots (expedientes-bot y Claude), nunca la cuenta del dueño.
- Respaldo activo (con el permiso del usuario): una tarea programada de Claude, «Respaldo del ciclo de Instagram (GitHub)», lanza el ciclo cada día a las 13:43 y a las 20:43 (hora de España), justo después de las publicaciones de las 13:40 y las 20:40. Solo avisa si algo falla.
- Arreglo definitivo, que solo puede hacer el dueño: GitHub › Actions › Ciclo Instagram › «…» › Disable workflow y después Enable workflow. Cuando aparezcan ejecuciones con event=schedule, la tarea de respaldo avisa de que ya se puede borrar.
- Consecuencia mientras tanto: las respuestas a comentarios y las estadísticas solo se actualizan en esas dos ejecuciones diarias (y en las manuales).

## 6/11/2026 (4.ª ejecución, programada) · Recorte de silencios en la voz y pausa antes del giro más corta

Comparación de retención: **todavía sin datos**. Ningún reel con Pocket TTS se ha publicado aún (003 sale hoy a las 13:40 y 002 a las 20:40). Se compara en la próxima ejecución frente a 001 (Piper).

Medición de los renders REALES de la release «cola» (002, 004, 005, voz Pocket): −14,6 / −15,3 / −15,5 LUFS, pico real −2,1 a −2,2 dBFS (todo bien). Pero en el 002 la mezcla cae a **−53 LUFS durante ~1 s** justo antes del giro (12,5-13,5 s): es el corte de música previo al giro (1,0 s) sumado a que la voz de la escena anterior ya había terminado. Casi un segundo de silencio digital: parece que el vídeo se ha cortado.

### Cambio 4: pausa antes del giro de 1,0 s a 0,5 s (herramientas/hacer_reel.py, constante `CORTE_GIRO`)
- La música y el lecho callan 0,5 s antes de la escena «giro» (antes 1,0 s). La subida de tensión dura 0,5 s más y llega hasta el corte. El golpe del giro no cambia.
- Prueba (ejemplo_guion.json, giro a 28,0 s): silencio de la música de 27,0→28,0 s (0,99 s) pasa a 27,5→28,0 s (0,49 s).
- Fuentes (solo patrones): fluxnote.io «Faceless Shorts retention tips 2026» (pausa de 0,5 s antes de la revelación clave, una por vídeo); blitzcutai.com «Dead air kills watch time» (pausas intencionadas de 0,3-0,5 s; los huecos largos hacen perder espectadores).
- Revertir: `CORTE_GIRO = 1.0` en hacer_reel.py.

### Cambio 5: recorte de silencios de cada frase de la voz (publicar_gh.py `recortar_silencios`, equipo/voz.json `recorte`)
- Antes de mezclar, a cada frase (Pocket o Piper) se le quita el silencio del principio y del final (deja 70 ms de margen) y las pausas internas de más de 0,5 s se dejan en 0,35 s. Umbral: −40 dB respecto al pico de la frase, ventanas de 20 ms, fundidos de 12 ms en cada corte (sin chasquidos). No toca pausas cortas ni la voz.
- Motivo: Pocket habla más pausado que Piper y necesitaba atempo de hasta 1,13 (prueba_voz.json) para caber en la escena; con menos silencio hace falta menos aceleración, la voz arranca nada más empezar la escena (estándar: voz en el primer segundo) y no quedan huecos muertos dentro de una frase. Fuente: syllaby.io «Voiceover pacing, silence trimming and retention editing» (pausas entre frases de 200-400 ms; recortar silencios de más de 300 ms).
- Prueba en la nube con voz SIMULADA (aquí Hugging Face está bloqueado; los niveles valen, el sonido no): conserva el 100 % de la energía de la voz, arranque a 90 ms, pausa interna de 0,9 s → 0,35 s, pausa de 0,45 s intacta. En la mezcla de ejemplo_guion.json recorta 0,3-0,7 s por frase y baja el atempo necesario entre 0,04 y 0,15. Vídeo 1080x1920 H.264+AAC, 36,9 s, pico real −2,0 dBFS; 5 fotogramas correctos.
- Si falla, la frase se queda como estaba y se anota en registro.log. Cuando actúa, registro.log muestra «Voz: silencios recortados por frase (s): [...]»: así se ve cuánto recorta con la voz real.
- Revertir: en equipo/voz.json poner `"recorte": {"activo": false}` (o borrar la clave). Código anterior: herramientas/versiones/publicar_gh.py_2026-11-06.

### Próxima ejecución
- Revisar en registro.log los segundos recortados con la voz real de Pocket. Si recorta más de 1 s en una frase o la voz suena entrecortada, subir `pausa_max_s` a 0,45 o bajar `umbral_db` a −45.
- Comparar ig_reels_avg_watch_time de 003/002 (Pocket, sin estos cambios) y de los siguientes (con ellos) frente a 001.
- Pendiente menor: el reloj del HUD vuelve a empezar en la tarjeta de cierre de los remasters.

### Petición de Calidad (6/11/2026, equipo/modelos_ganadores.md)
- hacer_reel.py: mostrar el gancho entero en el primer fotograma o escribirlo en ≤ 0,5 s (línea 231: hoy nchars/1,1 s, así que a 0,4 s solo se lee «UN BARCO INT»); añadir estilos visuales de prueba propia (mapa con ruta, línea de tiempo, contador animado) y una tarjeta final de recapitulación de 3 datos.

## 6/11/2026 (5.ª ejecución, extra pedida por el usuario) · Sello de veredicto para el ¿REAL O FALSO? sin metraje ajeno

Contexto: Calidad mandó 003 y 005 a revision/ porque el metraje de los reels antiguos tiene marcas de agua ajenas (iStock, Storyblocks, InVideo); estándar v2: esos ¿REAL O FALSO? se rehacen como reel nuevo con guion.json. Faltaba en hacer_reel.py un recurso visual para el veredicto.

### Cambio 6: campo opcional `"sello"` en las escenas de guion.json (herramientas/hacer_reel.py)
- `"sello": "FALSO"` (o "REAL", "MITO", "CONFIRMADO"...): un sello grande cae de golpe sobre la parte de arriba de la escena (de 2,3x a 1x en 0,13 s, con temblor de 4 fotogramas, destello y un golpe seco de sonido). Rojo para FALSO/MITO/BULO, verde para REAL/VERDADERO/CIERTO/CONFIRMADO, ámbar para lo demás. Por defecto cae a los 0,5 s en la escena «giro» (cuando la voz dice el veredicto) y a los 0,25 s en las demás; `"sello_t"` lo cambia.
- Va en y≈490 (zona del dibujo), no tapa la etiqueta ni el texto. Documentado en INSTRUCCIONES_EQUIPO.md (formato de guion.json).
- Motivo: el veredicto es el momento de «no me lo creo» del formato; un golpe visual y sonoro en el giro marca la revelación (fish.audio, «Using sound effects for short-form content»: golpe o «stinger» en las revelaciones; fluxnote.io: pausa y golpe en la revelación clave).
- Prueba: guion de prueba ¿REAL O FALSO? (koala coyote, 6 escenas, sellos FALSO y REAL) + voz simulada: 1080x1920 H.264+AAC, 24,7 s, pico real −2,0 dBFS; sin voz, −0,8 dBFS, igual que antes (el golpe no sube el pico). 5 fotogramas revisados: gancho completo a 1,2 s, sello legible y sin tapar la etiqueta. Un guion SIN `sello` da exactamente el mismo audio que antes (md5 idéntico).
- Revertir: no usar el campo, o copiar herramientas/versiones/hacer_reel.py_2026-11-06b (conserva la pausa de 0,5 s del cambio 4).

### Cambio 7 (misma ejecución): petición de Calidad, gancho en 0,45 s y recursos que prueban el dato (herramientas/hacer_reel.py)
- Gancho: se escribe entero en 0,45 s y sin retardo inicial (antes 0,5 s + 0,12 s de retardo, entero a ~0,62 s). Comprobado: a 0,45 s se lee completo.
- Campos opcionales nuevos por escena (documentados en INSTRUCCIONES_EQUIPO.md); si no se usan, el reel sale igual que antes:
  - `"cifra"` (+ `"unidad"`): contador animado grande con barra de progreso (0 → cifra en 1,3 s, respeta el punto de miles).
  - `"fechas"`: línea de tiempo de 2-4 hitos que se rellena durante la escena; el hito actual se agranda.
  - `"lista"`: hasta 3 puntos numerados que entran uno a uno (recapitulación final guardable).
  - El texto de la escena baja un poco (y 1060-1150) para dejar sitio; todo queda entre y≈400 y 1450, sin tapar etiquetas ni el sello CLASIFICADO.
- Motivo: equipo/modelos_ganadores.md (Calidad, 6/11): los grandes del nicho usan contadores, líneas de tiempo y mapas que prueban el dato; nuestras escenas eran decoración repetida; falta un recurso guardable al final.
- Prueba: guion de prueba de 5 escenas (gancho, cifra, fechas, sello REAL, lista) + voz simulada: 1080x1920 H.264+AAC, 22,9 s, pico real −1,9 dBFS; fotogramas revisados (contador a medias y completo, línea de tiempo, lista, sello), sin solapes.
- Pendiente: mapas (ruta entre lugares). Necesitan contornos de dominio público (Natural Earth) dibujados por código; aquí no hay red para descargarlos. Otra ejecución.
- Revertir: no usar los campos; para el gancho, poner `nchars / 0.5` y `self.delay = 0.35 if self.style == "giro" else 0.12`. Copia anterior: herramientas/versiones/hacer_reel.py_2026-11-06c.
- Petición al Remasterizador y al Creador: 006-009 (¿REAL O FALSO?, aún sin renderizar) no usan todavía `"sello"` ni los recursos de prueba. Recomiendo añadir `"sello":"FALSO"` en la escena del veredicto, una `"cifra"` o unas `"fechas"` en el dato central y una `"lista"` de 3 datos en el cierre, antes de que se rendericen.

## 6/11/2026 · Remasterizador (con permiso total del usuario): `"modo": "humano"` en herramientas/hacer_reel.py
Orden del usuario (6/11, PRIORIDAD MÁXIMA): ningún reel ha funcionado; humanizar al máximo, nada de efectos de plantilla. El Creador había escrito la especificación del modo humano en INSTRUCCIONES_EQUIPO.md pero hacer_reel.py no lo tenía. Implementado y probado:
- `"modo": "humano"` en guion.json: NO se dibuja el HUD (REC, CAM 02, SP▶LP, etiquetas INCIDENTE/EVIDENCIA…), ni el sello CLASIFICADO, ni ojos, siluetas, radar u onda, ni glitch, ni líneas de escaneo ni parpadeo. Grano muy leve.
- Cada escena lleva `"imagenes"` (1-3; `url`, `credito`, `mov` zoom_in|zoom_out|pan_izq|pan_der) con movimiento de cámara leve; se descargan con caché a ~/.cache/expedientes/imagenes/. Las fotos apaisadas van sobre sí mismas desenfocadas y oscurecidas. Si no hay fotos o la descarga falla, fondo neutro (degradado oscuro con deriva lenta): el render nunca se cae. El crédito sale pequeño a la derecha (y=1500).
- Subtítulos estilo creador PALABRA A PALABRA: grupos de 2-4 palabras cortados por la puntuación, grandes, blancos, centrados, la palabra actual en amarillo; ritmo 2,6 palabras/s desde +0,12 s (la voz se mezcla después con 120 ms de retardo, así que van aproximadamente a la par). Texto de los subtítulos: `"subtitulos"` si existe (para escribir 1936 en vez de «mil novecientos treinta y seis»), si no la propia `"voz"`. En el gancho, el `"texto"` entero desde el primer fotograma (3 líneas como mucho). En las demás escenas, `"texto"` = rótulo corto fijo arriba (y≈470-580, dentro de la zona segura).
- Audio: sin lecho de tensión (drone) ni golpes ni subida; la música queda a −31 LUFS antes de la voz (antes −24) y sin bombo. El corte de 0,5 s antes del giro se mantiene (es una pausa natural).
- No se dibujan en modo humano: `sello`, `cifra`, `fechas`, `lista` (son gráficos de plantilla). Si Calidad los quiere, hay que rehacerlos con el estilo limpio (lista numerada en tipografía sencilla sobre la foto) — pendiente para Mejora.
- Pruebas: 010 (35,0 s) y 011 (35,2 s) renderizados en la nube con fondo neutro; guion de prueba con foto apaisada, foto vertical, rótulo, subtítulos con cifra y URL inválida (cae al fondo neutro sin error). 1080x1920 H.264+AAC, −31 LUFS sin voz. Un guion SIN `"modo"` renderiza exactamente igual que antes (el modo solo cambia el flujo cuando está activo).
- Revertir: quitar `"modo"` de los guiones (no hace falta tocar código) o copiar herramientas/versiones/hacer_reel.py_2026-11-06d.
- PETICIONES A MEJORA (lo que de verdad falta para que parezca humano):
  1. Sincronía real de los subtítulos: generar la voz ANTES del render (hoy publicar_gh.py la mezcla después) y pasar a hacer_reel.py los tiempos por palabra (Pocket TTS o un alineador tipo whisper-timestamped); mientras tanto los subtítulos van a 2,6 palabras/s estimadas.
  2. Fotos reales: desde la nube de los agentes no se llega a Wikimedia Commons (proxy bloquea commons.wikimedia.org y upload.wikimedia.org), así que no se pueden verificar licencias ni probar la descarga aquí. Conviene un script en GitHub Actions (`herramientas/buscar_imagenes.py`) que consulte la API de Commons (extmetadata: LicenseShortName, Artist) y escriba en post.json `_imagenes` con la licencia, para que Creador y Remasterizador solo elijan entre candidatos ya verificados.
  3. La voz sigue siendo sintética (Pocket TTS, lola). Es el mayor freno de humanización: probar entonación más conversacional (temperatura, frases con puntos suspensivos) y, si el usuario puede, grabar él la voz de los ganchos.

## 6/11/2026 · Calidad (orden del usuario «pon todo al máximo»): buscador de imágenes reales en GitHub Actions
Resuelve la petición 2 del Remasterizador (desde la nube de los agentes, Commons está bloqueado).
- herramientas/buscar_imagenes.py + .github/workflows/imagenes.yml (solo se lanza al cambiar equipo/busqueda_imagenes.json o a mano; no toca publicar_gh.py ni ciclo.yml, no publica nada).
- Consulta la API de Commons, se queda solo con dominio público, CC0 y CC BY (descarta BY-SA, NC, ND), ≥ 500 px, y escribe equipo/imagenes_candidatas/<tema>.json con URL lista para guion.json, licencia, autor y crédito. Sube a la release «pruebas» una hoja de contactos numerada (imagenes_<tema>.jpg) para verlas antes de elegir.
- Probado: 1.ª ejecución 11:56 UTC, 8 temas, 22-30 candidatas por tema, éxito en 2 min. Con ellas se rehicieron 010, 002, 011 y 004.
- Revertir: borrar el workflow y el script; nada más depende de ellos.

## 6/11/2026 · Voz del dueño clonada desde sus reels de Mr. Empírico (orden directa del usuario)
- Autorización por escrito del dueño (6/11/2026): «los vídeos subidos son todos míos, soy yo el protagonista, clona mi voz de esos vídeos de Mr. Empírico».
- Nuevo workflow manual .github/workflows/voz_usuario.yml + herramientas/voz_usuario.py: descarga los 10 reels más vistos del podcast Empírico (Graph API), separa la voz de la música con Demucs, transcribe con faster-whisper, agrupa los tramos por hablante (Resemblyzer) y monta voces/referencia_usuario.wav (~11 s) y la versión larga (~30 s) con el hablante que más habla. Las sube a la release privada «voces». Después prueba Chatterbox con esa referencia (variantes chatterbox_usuario, chatterbox_usuario_suave y chatterbox_mtl_usuario de prueba_voz.py, con Pocket de control) y mide el parecido (coseno Resemblyzer). Informe: equipo/pruebas/voz_usuario.json.
- ciclo.yml descarga voces/referencia_usuario.wav de la release cuando el motor principal es Chatterbox. voces/ va en .gitignore (nunca audio en git).
- Pendiente: pasar equipo/voz.json a "motor": "chatterbox" (respaldo pocket, piper) cuando la prueba dé un parecido ≥ 0,5 y una inteligibilidad (WER) ≤ 0,15.

## 6/11/2026 (Mejora, 2.ª sesión en paralelo) · Clips de VÍDEO REAL en el modo humano (petición 2 de plan.json y orden del usuario «uso prioritario de vídeo real»)
Hasta ahora el modo humano solo admitía fotos con movimiento de cámara. Ahora una escena puede llevar vídeo real:
- herramientas/hacer_reel.py: en `"imagenes"` una entrada puede ser `{"video": url|ruta, "inicio": s, "credito", "mov"}`. El clip se descarga con caché (~/.cache/expedientes/videos/, tope 200 MB), ffmpeg extrae solo los fotogramas de su tramo (a 30 fps, sin audio, encajado como las fotos: los verticales llenan el lienzo, los apaisados van sobre sí mismos desenfocados y oscurecidos) y se le aplica el mismo zoom leve que a las fotos (`mov` solo zoom_in | zoom_out | fijo; sin paneo, porque el vídeo ya se mueve). Si el clip es más corto que su tramo se repite en bucle; `inicio` fuera del clip vuelve a 0. Rutas relativas: respecto a la carpeta del guion. Los fotogramas temporales se borran al terminar (atexit).
- publicar_gh.py `resolver_videos_guion` (solo en reels nuevos, antes de `renderizar_guion`): una entrada `{"original_id": "<id de originales/>"}` descarga ese reel propio del usuario con la API (media_url) a la carpeta de trabajo y escribe `guion_resuelto.json` con la ruta local; las rutas relativas de `"video"` se vuelven absolutas. Si Instagram no da el vídeo (música con licencia, id erróneo) se anota en registro.log y la escena sigue con su foto o el fondo neutro. Un guion sin vídeos ni original_id no se toca.
- Pruebas en la nube (voz simulada): clip apaisado 1280x720 (fondo desenfocado + zoom_out), clip vertical de 2 s en una escena de 6,8 s (bucle), `original_id` resuelto por una API simulada, `original_id` sin media_url (cae a fondo neutro con aviso), URL de vídeo rota y ruta relativa. 1080x1920 H.264+AAC; los fotogramas del clip avanzan (diferencia media 12 entre 6 s y 9 s); el crédito sale como en las fotos. REGRESIÓN: un guion sin clips produce un mp4 con el mismo md5 que antes del cambio.
- Lo que NO se puede probar aquí: la descarga real desde Commons / Instagram (proxy bloqueado); se verá en el primer render de Actions con un clip. Si falla, el reel sale igualmente (con fotos o fondo neutro).
- Para el Creador y el Remasterizador: en los ¿REAL O FALSO? de segunda vida (010, 013…) se puede poner la escena de apertura con `{"original_id": "<id del reel antiguo>", "inicio": <segundo del pico>}` en vez de una foto, SOLO si el fotograma está limpio de marcas ajenas. Documentado en INSTRUCCIONES_EQUIPO.md (modo humano).
- Revertir: no usar `"video"` ni `"original_id"` (sin esos campos el render es idéntico), o copiar herramientas/versiones/hacer_reel.py_2026-11-06e y publicar_gh.py_2026-11-06c (ojo: esta última copia es anterior a los cambios de voz de la otra sesión de Mejora de hoy; mejor quitar solo `resolver_videos_guion` y su llamada en `renderizar`).
- Coordinación: la otra sesión de Mejora de hoy lleva la voz (Chatterbox/Kokoro, voz del dueño, prueba_voz #4); esta sesión no toca voz.json ni los motores para no pisarla.

## 6/11/2026 (Mejora, sesión de voz, ejecución programada) · Chatterbox sustituye a Pocket/Piper como voz predeterminada + flujo «voz primero»

Orden del usuario (6/11): humanizar al máximo; sustituir Piper por un TTS moderno, gratuito y con licencia comercial (Chatterbox primero, Kokoro como alternativa rápida; nada CC-BY-NC/CPML). Comparación de retención de los cambios anteriores: **todavía sin datos** (ningún reel con Pocket se ha publicado aún; 002 sale hoy a las 20:40).

### Licencias comprobadas
- Chatterbox (Resemble AI): código y pesos MIT (github.com/resemble-ai/chatterbox; ficha HF ResembleAI/Chatterbox-Multilingual-es-es «License: mit», archivos t3_es_es.safetensors + s3gen_v3 + tokenizer). Lleva marca de agua inaudible Perth (no afecta). Sin atribución obligatoria; el post lleva «Voz generada por IA» (Meta pide marcar audio realista generado).
- Kokoro-82M (hexgrad): Apache 2.0, voces españolas ef_dora / em_alex / em_santa (voces del propio modelo, de nadie real).
- Referencia de voz para Chatterbox: NO hay audio del usuario en el repo todavía (la otra sesión de Mejora lo está sacando de sus reels con su autorización; release «voces»). Mientras tanto la referencia es un clip de 10 s en español generado con Kokoro em_alex (`referencia_kokoro`), que se genera en el propio runner y se cachea (~/.cache/expedientes/voces/): licencia libre, ninguna persona real. En cuanto exista voces/referencia_usuario.wav, publicar_gh.py la usa automáticamente (tiene prioridad sobre la de Kokoro).

### Cambio 8: motores de voz nuevos y cadena de respaldo (publicar_gh.py, herramientas/voz_chatterbox.py, voz_kokoro.py, ciclo.yml, equipo/voz.json)
- equipo/voz.json: `"motor": "chatterbox"`, `"respaldo": ["kokoro", "pocket", "piper"]` (toda la locución sale del mismo motor; si uno falla o se pasa de `max_s`, se prueba el siguiente y queda en registro.log «Voz X no disponible…»).
- Chatterbox va en su propio venv (~/.venvs/chatterbox, fija torch 2.6 / transformers 4.46; `PYTHON_CHATTERBOX`), en CPU, con el afinado es-es cargado sobre el multilingüe v3 (si no encaja, usa el multilingüe con language_id=es y lo dice en el log: `modelo_usado`). Ajustes: exageración 0,6, cfg 0,35, temperatura 0,75, semilla fija 7. Guardia contra alucinaciones: si una frase dura más de 1,6× lo esperable por sus palabras, se regenera con otra semilla (máx. 2 veces) y queda en el log.
- ciclo.yml: Python 3.11 cuando hay motores neuronales; instala solo lo que pide la cadena (Chatterbox solo si es principal; Kokoro/Pocket también como respaldo); caché `voz-v2-*` de ~/.cache/huggingface, pocket_tts y pip; timeout 60 min.
- Coste: Chatterbox tarda ~6 min por reel de 8 frases en el runner (4 CPU): 331-378 s de síntesis. Kokoro 18-26 s. Pocket 18-21 s. Piper 8 s. Dentro del límite (`max_s` 1500) y del ciclo (2 renders por pasada).

### Cambio 9: «voz primero» (publicar_gh.py `renderizar_guion`, hacer_reel.py `--solo-locucion` / `--tiempos`)
- Antes: se renderizaba el vídeo con escenas estimadas a 2,6 palabras/s y después la voz se ACELERABA (atempo hasta 1,35) para caber, y los subtítulos iban a un ritmo estimado (petición 1 del Remasterizador).
- Ahora, en los reels nuevos (guion.json): 1) hacer_reel.py --solo-locucion escribe los tramos sin dibujar nada; 2) se genera y recorta la voz; 3) hacer_reel.py --tiempos recibe la duración real de cada frase: la escena se alarga a voz + 0,45 s (nunca se acorta por debajo de lo que pide el guion) y los subtítulos palabra a palabra van al ritmo real de ESA frase; 4) se mezcla. Resultado en la prueba: atempo 1,00 en las 8 frases con todos los motores (antes el 002 llevaba hasta 1,13). Si el paso 1 falla, se hace como antes. Los remasters no cambian.
- Probado en la nube con voz simulada (lenta, 2 pal/s): las 8 escenas se alargan, atempo 1,0, 1080x1920 H.264+AAC, 5 fotogramas correctos, pico −5,9 dBFS; y en el runner con los 7 motores reales (abajo).

### Prueba real (GitHub Actions, run 42264747098, 4 CPU, guion herramientas/ejemplo_guion_humano.json = cola/004 Mary Celeste, 8 frases, 104 palabras) → equipo/pruebas/prueba_voz.json; vídeos y mp3 de voz sola en la release «pruebas»
| Variante | Síntesis | UTMOS (1-5) | WER voz sola | Tono: desv. / rango (semitonos) | Pausas | Pal/s | Observaciones (transcripción Whisper) |
|---|---|---|---|---|---|---|---|
| pocket_antes (flujo viejo, lola) | 21 s | 3,83 | 21,2 % | 2,0 / 5,2 | 32 % | 2,71 | **mete sílabas inventadas** («el triba Xie», «que Jévi», «que encioremos hija», «que emance») en 4 de 8 frases |
| piper davefx | 8 s | 2,89 | 19,2 % | 3,1 / 8,2 | 17 % | 3,27 | robótica, «suven», «solo salta» |
| pocket (voz primero) | 18 s | 3,98 | 18,3 % | 2,0 / 5,5 | 34 % | 2,65 | mismas sílabas inventadas |
| kokoro_alex | 26 s | 3,64 | **8,7 %** | 3,3 / 8,6 | 15 % | 3,18 | limpia, pero ritmo de lector: ignora los «…» |
| kokoro_dora | 18 s | 3,81 | **8,7 %** | 2,9 / 7,7 | 17 % | 3,24 | ídem, voz femenina |
| chatterbox_es (voz integrada inglesa) | 331 s | 3,32 | 14,4 % | 6,7 / 17,1 | 16 % | 3,24 | acento («vaco», «Mérice Leste»), añade «Bueno,» |
| **chatterbox_es_ref (referencia Kokoro em_alex)** | 378 s | 3,60 | 10,6 % | **4,0 / 9,9** | **23 %** | **2,87** | limpia; respeta los «…»; única con perfil de conversación |
| chatterbox_mtl (multilingüe, voz integrada) | 273 s | 3,81 | 12,5 % | 5,3 / 14,2 | 20 % | 3,24 | «parco», «Mery», añade «Ah,» |

Referencias orientativas de habla conversacional: 2-4 semitonos de desviación del tono y 15-25 % de pausas; lectura plana < 2 semitonos (medido con librosa pyin sobre la voz sola; UTMOS22 es un predictor entrenado sobre todo en inglés, orientativo: le da la nota más alta a Pocket, que es justo la que inventa sílabas).

### Decisión (de oído razonado, no escuchado: aquí no hay altavoz; el usuario tiene los mp3 para elegir)
- **Predeterminada: Chatterbox es-es con referencia Kokoro em_alex** (`chatterbox_es_ref`). Es la única que suena a alguien contando algo: hace las pausas de los puntos suspensivos (23 % de pausa, 2,9 pal/s frente a 3,2 de Kokoro), varía el tono como una conversación (4 st) sin pasarse (la voz integrada se dispara a 6,7 st y mete palabras), y pronuncia limpio (WER 10,6 %, sin sílabas inventadas). Se descarta Pocket (predeterminada hasta hoy) porque inventa sílabas en la mitad de las frases: es el artefacto de IA más delatador. Kokoro es la mejor en pronunciación (8,7 %) y 15 veces más rápida, pero lee de carrerilla: queda de primer respaldo.
- Revertir: en equipo/voz.json `"motor": "kokoro"` (rápido y limpio) o `"motor": "pocket"` (como el 5/11); `"respaldo"` queda igual. Para desactivar el flujo voz primero sin tocar código: no hay interruptor; copiar herramientas/versiones/publicar_gh.py_2026-11-06b y hacer_reel.py_2026-11-06d (ojo: deshace también los clips de vídeo de la otra sesión; mejor quitar solo la llamada a `renderizar_guion` en `renderizar`).

### Próxima ejecución
- Escuchar un render real de la cola con Chatterbox (release «cola») y leer en registro.log «Voz con Chatterbox (es-es…)»: si pone `modelo_usado` multilingue o aparecen «frases regeneradas por duración anómala» repetidas, revisar. Si el usuario elige otra muestra, cambiar `"motor"` (y `kokoro.voz`) en voz.json.
- Cuando la otra sesión suba voces/referencia_usuario.wav a la release «voces», el ciclo la usará en el siguiente render: comprobar WER y que no salga con acento; si empeora, poner `"referencia": null` en voz.json (y queda la de Kokoro).
- Comparar ig_reels_avg_watch_time de los reels con Chatterbox frente a 001 (Piper) y 002/003 (Pocket).
- Pendiente menor: en el modo humano el rótulo superior tapa texto cuando la foto es un recorte de periódico (fotograma 33 s del 004): bajar la opacidad de la foto bajo el rótulo o subir el rótulo.
- 6/11 19:40 (misma sesión) · Para la sesión de la voz del dueño: ya existe voces/referencia_usuario.wav en la release «voces» y ciclo.yml la descarga, así que en producción se habría usado SIN probar. He dejado `"referencia": null` en voz.json (se usa la referencia Kokoro) hasta que vuestra prueba (chatterbox_usuario / _suave) dé parecido ≥ 0,5 y WER ≤ 0,15; entonces poned `"referencia": "voces/referencia_usuario.wav"` (y, si procede, cambiad la marca «Voz generada por IA» de publicar_gh.py `ATRIBUCIONES` por «Voz: generada a partir de la voz del autor»). Ojo también: el ciclo YA se ha disparado por `schedule` (run 42267323112, 18:04 UTC), así que el respaldo de Claude de las 13:43/20:43 se puede retirar cuando se confirme que se repite.

- 6/11 19:40 (Calidad, petición a Mejora) · En los renders de las 15:00 UTC, 002 (escena «A la semana retiran…») y 010 (cierre) salieron con fondo neutro negro porque una foto no se descargó en Actions (a2/Australian_soldiers_resting… y a8/Colored-Crop-Tasmanian_tiger.jpg; los hash de ruta son correctos, así que parece fallo transitorio o de tamaño). Es bloqueo 7a para el usuario. Pedido: (1) en hacer_reel.py, reintentar la descarga 2-3 veces con pausa y, si una escena se queda sin fotos, reutilizar la última foto cargada (de la escena anterior o siguiente) en lugar de `fondo_neutro`; (2) anotar en registro.log la URL que falla («Imagen no descargada: …») para poder corregirla; (3) idealmente cachear las fotos en la release «pruebas» junto a la hoja de contactos. Mientras tanto Calidad añade una foto de respaldo a las escenas con una sola foto cuando ha visto el fallo.
- 6/11 19:40 (sesión de la voz del dueño) · El dueño ha confirmado que su voz es la «voz A» = hablante 1 de equipo/pruebas/voz_usuario.json (reel del Proyecto ALCAYATA, 18179330035291210). La voz B (Mr. Tartaria, 18085269121411497/18048020833521161) NO es suya: voz_usuario.py ya no la guarda y el workflow borra referencia_hablante_2.wav de la release. Hallazgo: la Graph API da sin pista de audio (solo h264) varios reels de 2024, entre ellos el viral 18018636716017127; solo 3 de 10 tenían audio. La ejecución 3 (lanzada por push) se quedó colgada en apt-get y se canceló; se relanza con valores por defecto válidos para el disparo por push (antes, sin inputs, prueba_voz corría todas las variantes).

## 6/11/2026 (Mejora, 2.ª sesión, tras escuchar el usuario las muestras: «hay que mejorar mucho todavía, falta gancho y énfasis»)

### Cambio 10: intensidad por estilo de escena (publicar_gh.py `ajustes_por_estilo`, voz_chatterbox.py, voz_kokoro.py, equipo/voz.json)
- hacer_reel.py escribe en cada tramo de locucion.json el `estilo` de su escena; publicar_gh.py lo pasa al motor y cada frase lleva sus propios ajustes según `equipo/voz.json → <motor>.por_estilo`. Hoy: Chatterbox gancho exageración 0,85 / cfg 0,3; giro 0,8 / 0,3; cierre 0,7; el resto 0,6 / 0,35. Kokoro: gancho a 0,88 de velocidad y giro a 0,9 (más lento = más peso).
- Motivo: la muestra que oyó el usuario llevaba la misma intensidad en todas las frases; el gancho sonaba como una frase más.
- Revertir: borrar `por_estilo` de voz.json.

### Cambio 11: *énfasis* marcado en el guion (hacer_reel.py `parsear_enfasis`, publicar_gh.py `aplicar_enfasis` + `realce_enfasis`)
- En "voz" (y en "texto" del gancho) las palabras entre asteriscos son el énfasis: `Solo falta *una* cosa. *El bote salvavidas*.` El motor recibe el texto limpio. Con la alineación (cambio 12) esas palabras suben +3,5 dB (filtro `volume` de ffmpeg con línea de tiempo, DESPUÉS de la cadena de compresión para que el compresor no lo aplaste) y llevan un respiro de 90 ms delante del grupo (silencio insertado en el wav, tiempos de las palabras siguientes desplazados). En los subtítulos salen en rojo (255,82,58), también en el gancho entero.
- Ajustes en voz.json `enfasis`: `db`, `pausa_ms`, `db_previo` (0), `activo`.
- Revertir: `"enfasis": {"activo": false}` (los asteriscos siguen saliendo en rojo en los subtítulos) o no marcar nada.

### Cambio 12: alineación palabra a palabra de la voz real (herramientas/alinear_voz.py, faster-whisper «small» int8 en CPU; ciclo.yml instala faster-whisper cuando hay motores neuronales)
- Tras recortar silencios, cada frase se transcribe con marcas de tiempo por palabra y se casa con las palabras del guion (difflib; «mil ochocientos setenta y dos» ↔ «1872» se reparte en el mismo tramo; las palabras que Whisper no oye se interpolan; si casan menos de la mitad, esa frase se queda con la estimación). Los tiempos van a hacer_reel.py en `--tiempos` como `{"escena": {"dur": s, "palabras": [[ini, fin], ...]}}` y los subtítulos palabra a palabra entran 60 ms antes de oírse cada palabra (ya no a 2,6 palabras/s estimadas: petición 1 del Remasterizador resuelta).
- Si falta faster-whisper o falla, registro.log dice «sin alineación por palabra» y todo sigue como antes (sin realce de volumen, subtítulos al ritmo real medio de la frase). Ajustes en voz.json `alineacion` (`modelo`, `max_s`, `activo`).
- Coste estimado en el runner: modelo small int8 ≈ 15-30 s por reel (modelo cacheado con ~/.cache/huggingface).

### Cambio 13: el gancho va a pelo (hacer_reel.py `make_audio`, solo modo humano)
- La música no suena durante la primera escena y entra en fundido de 0,8 s cuando acaba (medido sobre el render sin voz: −70 LUFS en los 4 primeros segundos, −31,7 LUFS después). Así la primera frase es solo la voz, como cuando alguien te suelta algo a la cara. Revertir: quitar el bloque `if MODO["humano"] and hook_end < total - 2.0` en make_audio.

### Pruebas en la nube (voz simulada con tiempos de palabra conocidos, que aquí sustituye a faster-whisper)
- Flujo completo: estilos llegan al motor (`['gancho', 'archivo', ..., 'giro', ..., 'cierre']`), 8/8 frases alineadas, énfasis aplicado (gancho +0,09 s por el respiro; giro +0,18 s por dos grupos), tiempos por palabra en tiempos_voz.json, render 1080x1920, pico −2,2 dBFS con la cadena completa. Medido sin cadena: «una» (énfasis) +3,4 dB y «El bote salvavidas» +3,7 dB frente a las palabras vecinas; con la cadena la mezcla no falla (no aparece «Cadena de voz descartada»).
- Fotogramas: gancho entero con «sin nadie» en rojo desde el primer fotograma; «y está todo.» con «todo.» en rojo; giro «El bote» en rojo.
- Fallo encontrado y corregido en la misma prueba: los tramos que se releen tras el segundo render no llevaban los tiempos por palabra, así que el realce no se aplicaba en la mezcla; ahora se copian de los tramos alineados.
- Un guion clásico (sin modo humano) sigue escribiendo su locución igual (`estilo` y `enfasis: []` añadidos, inofensivos).
- herramientas/ejemplo_guion_humano.json lleva ya marcas de énfasis (gancho, evidencia, giro y «nada»).
- Prueba real lanzada en Actions (prueba_voz.yml, variantes chatterbox_es_ref y kokoro_alex) para enviar al usuario el reel de después con la voz real. Resultado: ver más abajo.
- Revertir todo: copiar herramientas/versiones/hacer_reel.py_2026-11-06f, publicar_gh.py_2026-11-06d, voz_chatterbox.py_2026-11-06, voz_kokoro.py_2026-11-06, voz.json_2026-11-06c y ciclo.yml_2026-11-06b.
- 6/11 20:50 (misma sesión) · **Producción comprobada**: el ciclo 42270658374 renderizó 010 y 002 con `Voz con Chatterbox (es-es, referencia=sí…)` en 412 y 354 s (9 y 8 frases), sin caer al respaldo; 1080x1920 H.264 High + AAC 44,1 kHz, 37,9 s, 13,6 MB. Pero **010 falló al publicar** (reel de prueba): la subida devolvió `ProcessingFailedError: Request processing failed` (el 001, reel normal, se publicó bien con la misma mezcla). Cambios: a) la mezcla final lleva `-movflags +faststart` (Meta recomienda el átomo moov al principio; comprobado: ftyp-moov-free-mdat); b) `publicar_reel`: si un contenedor de prueba falla al subir/procesar, se reintenta al momento como reel normal (probado con API simulada: prueba falla → normal publica; normal sin cambios). Queda 1 intento de los 3 para el 010 en el próximo ciclo; si vuelve a fallar como reel normal, el problema no es el trial reel y habrá que mirar el vídeo (Monetización/Analista). Revertir: quitar el `try/except` alrededor de `subir_y_esperar` en `publicar_reel` y el `-movflags`.
- RESULTADO REAL (Actions run 42273101879, 18:47 UTC, guion con marcas de énfasis): alineación 8/8 frases en 17 s con Kokoro y 8/8 en 18 s con Chatterbox (faster-whisper small, CPU). Chatterbox es-es + referencia Kokoro con intensidad por estilo: WER 8,7 % (antes 10,6 %), tono 4,6 st de desviación / 10 st de rango (antes 4,0 / 9,9), pausas 25 %, 2,84 pal/s, −15,5 LUFS, pico −2,0 dBFS, síntesis 243 s. Kokoro em_alex: WER 8,7 %, tono 3,2 st, 14 s de síntesis. Fotogramas: gancho entero con «sin nadie» en rojo sobre la foto real (Aivazovski, dominio público), subtítulos a la par de la voz. Reels enviados al usuario (versión 2). Los 4 reels de la cola que la otra sesión mandó rehacer se renderizarán ya con esto.
- 6/11 21:25 (Mejora, sesión de voz) · **Respuesta a Calidad (fotos que no se descargan → escena en negro)**, herramientas/hacer_reel.py `descargar_imagen` y `preparar_humano`: a) cada foto se reintenta 3 veces (0, 1 y 3 s); b) si un ORIGINAL de upload.wikimedia.org/wikipedia/commons falla o pesa más de 40 MB, se prueba su miniatura de 1280 px (`url_miniatura_commons`; los originales de Commons pueden ser enormes: ese es el caso probable de Colored-Crop-Tasmanian_tiger.jpg); c) si aun así una escena se queda sin foto, repite la última foto real de la escena anterior con otro movimiento de cámara (y su crédito) en vez del fondo neutro; el fondo neutro solo queda para un guion sin ninguna foto. Probado en la nube con descargas simuladas (escena 2 sin foto → reutiliza la de la 1, fotograma comprobado). Guardia de Chatterbox: umbral de duración relajado para frases cortas con punto interno («Falso. Lo inventamos nosotros.» tardó 4,4 s legítimos y se regeneraba sin necesidad). Revertir: copiar herramientas/versiones/hacer_reel.py_2026-11-06f.
