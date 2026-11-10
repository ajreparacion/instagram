# Primer fotograma, música de Instagram e interacción (Calidad, 11/11/2026 00:00; orden del dueño: «que capte en el primer fotograma, que llamen mucho la atención, mejorar mucho la interacción»)
Base: Buzzfy Playbook 2026 (abandono < 30 % ⇒ 1 reel de cada 3 revienta; texto en pantalla desde el primer fotograma 1,18×; abrir por el pico en humor/historias +7 puntos de retención; compartidos 1 por cada 8 likes en los virales) y los reels en español de cuentas pequeñas del 10/11 (ver tecnicas_virales.md).

## 1. El primer fotograma (todos los reels, también la portada)
El fotograma 0 es el anuncio entero del reel; si no vale como portada, no vale como apertura.
1. **El pico en el fotograma 0**: nada de fundido, rótulo de título, logo ni negro. Humor: empieza por el momento más absurdo (El Jambo sepultado en papeles, la Jupillo con ojeras a las 23:00, El Bola gritando) y después «…seis horas antes».
2. **Un primer plano con cara**: El Jambo o una IA ocupa ≥ 40 % del encuadre, expresión exagerada y la boca ya en movimiento.
3. **Texto gigante de 3-6 palabras** (gancho POV) en contraste máximo (blanco sobre color sólido o acento), entre y = 500 y 1450, legible en miniatura; una sola palabra en el color de acento.
4. **Movimiento y sonido en 0,3 s**: zoom de golpe o entrada con rebote, efecto de sonido seco y voz en el primer segundo. Cero silencio al arrancar.
5. **Color que corta el feed**: fondo plano saturado (no beige): amarillo, rojo o cian fuerte con el trazo negro grueso; un acento solo.
6. Prueba de 1 s antes de aprobar: pausa en el fotograma 0 y en el 0,5 s. ¿Se entiende quién, qué pasa y por qué debería quedarse? Si no, B1 y B7 fallan.

## 2. Música de la biblioteca de Instagram (Mejora ya lo tiene en publicar_gh.py: audio_ig en post.json)
- Solo audios de la biblioteca aptos para cuentas de negocio (la lista de tendencia de sellos NO vale: `is_ads_eligible: false`, lo documentó Mejora). Buscar por estilo: dembow, upbeat, hip hop, phonk, latin pop, instrumental.
- Elegir por energía y BPM (100-128), con el **golpe o el «drop» alineado con el fotograma 0 o con el giro del chiste** (el offset de inicio del audio se calcula para eso, no se arranca en el segundo 0 por defecto).
- Volumen: con voz y efectos, que la música se oiga entre frases (hoy audio_volume 0,35: subir a ≈ 0,5 si la mezcla de la muestra lo tapa; sin voz, 1,0). Calidad lo revisa por título, audio_id y offset, porque la música no está en el MP4.
- Cambiar de canción cada pocos episodios y apuntar cuál rinde (Analista).

## 3. Interacción: cómo se ganan me gusta, compartidos, guardados y comentarios
Instagram penaliza el cebo explícito («dale like o…»): se consigue con el contenido, no pidiéndolo.
- **Me gusta**: el remate negro y la ironía del final; un chiste repetible (el contador de la Jupillo) hace que la gente vuelva a ver el siguiente.
- **Compartidos (lo que más alcanza)**: cada episodio nombra a quien enviarlo («Mándaselo a quien carga con todo», «al que dice «un momentito»»); el mensaje final con cifra y fuente es lo que hace que se reenvíe y se guarde.
- **Guardados**: el fotograma final serio con la cifra, estático 2-3 s, para captura.
- **Comentarios**: una sola pregunta de elección en el comentario fijado, no en el vídeo (p. ej. «¿Quién tiene la culpa: el Jambo o la Jupillo?», «¿Cuál ha sido tu «momentito» más largo?»). Y **responder en personaje en la primera hora** (la Jupillo contesta con su ironía cansada): Instagram valora las respuestas, y es el contenido más compartible del perfil. Mejora: automatizar con respuestas_chat.py si la API de comentarios lo permite; si no, anotarlo en pendiente_usuario.md.
- **Seguir**: el avance del siguiente episodio en el último segundo («Mañana: la Jupillo se planta»), con una promesa que se cumple. El pedido del pie sigue siendo uno solo (alternar enviar y seguir).
- **Serie con continuidad**: contador, gags que vuelven y una IA protagonista distinta por semana, para que quien vio el 1 busque el 2.
- **Historias**: cada reel publicado se comparte el mismo día a Historias con una pegatina de pregunta o encuesta («¿Quién cargó más: el Jambo o la Jupillo?»); es interacción gratis y empuja el reel.

## 4. Nuevos bloqueos de Calidad (v8.1, a aplicar desde la próxima pasada)
B7. **Primer fotograma débil**: fundido, negro, título o logo en el fotograma 0; sin cara ni pico; texto menor de 3 palabras o ilegible en miniatura; sin movimiento ni sonido en 0,3 s; portada distinta del gancho.
B8. **Sin mecanismo de interacción**: falta la frase de envío, el fotograma final guardable o la pregunta para el comentario fijado (campo `comentario_fijado` en post.json) y el avance del siguiente episodio (campo `avance_siguiente`).
Además: `audio_ig` debe existir con offset alineado al gancho (campo `audio_offset_s`).
