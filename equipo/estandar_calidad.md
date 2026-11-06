# Estándar de calidad de @nosabesloquehasvisto

Lo mantiene el agente de CALIDAD (lo revisa cada semana estudiando reels virales del nicho). Creador y Remasterizador lo leen antes de producir. Ningún reel se publica si no pasa este estándar.

Versión 4 (6/11/2026). (v3 y v2: 6/11; v1: 5/11/2026.) Base: cambios del algoritmo de Instagram en 2026 (los compartidos por mensaje y la retención pesan más que los likes; desde abril de 2026 se penaliza a las cuentas que resuben contenido sin edición material) y patrones de reels sin rostro de misterios y curiosidades.

## Bloqueos (si falla uno, NO se publica)
1. Algún dato no verificado con al menos 2 fuentes, o una cifra, fecha o nombre que no coincide con las fuentes.
2. Texto ilegible en algún momento (tamaño, contraste, cortado o tapado por la interfaz de Instagram).
3. Audio con distorsión, voz que se solapa o se corta, o silencio largo no intencionado.
4. Contenido ajeno (vídeo, imagen o música de terceros) o marcas de agua. Atención en los remasters: los reels antiguos de la cuenta llevan metraje de archivo con marcas de agua de terceros (iStock/Getty, Storyblocks, InVideo, «Grandes Misterios»), subtítulos quemados y pegatinas de encuesta. Si en el recorte se ve cualquiera de ellos, es bloqueo.
5. Temas vetados: consejos de salud, tragedias recientes con víctimas, acusaciones a personas reales vivas, desinformación.
7. (v4, ORDEN DEL USUARIO 6/11) Suena o se ve artificial o de plantilla. Es bloqueo cualquiera de estos:
   a) Ninguna imagen o vídeo REAL en alguna escena (también cuando una descarga falla y el render cae a fondo neutro; se detecta mirando un fotograma cada 2 s: fondo negro/degradado con solo subtítulos; fondo neutro, degradado, HUD «REC/CAM», sellos «CLASIFICADO», siluetas, polígonos, ojos u órbitas generados). Cada escena lleva foto o clip real con licencia comprobada y cambia cada 2-4 s.
   b) Voz de locutor o robótica: frases leídas de papel, misma entonación en todas, ritmo plano, sin pausas ni reacciones. Debe sonar a alguien contándoselo a un amigo.
   c) Texto con muletillas de IA («sumérgete», «descubre», «en este vídeo», «fascinante», «impactante», «adéntrate») o más de 2 emojis en el post.
   d) Aprobaciones caducadas: un calidad.json aprobado vale solo para el render que se revisó. Si el guion o el vídeo cambian, Calidad vuelve a revisar.
   e) Imágenes solo de dominio público, CC0 o CC BY, con crédito en pantalla y licencia en "_imagenes" de post.json. CC BY-SA no: con zoom y recorte el reel es obra derivada y la cláusula «compartir igual» no se puede cumplir en Instagram. Se buscan con herramientas/buscar_imagenes.py (workflow «Buscar imágenes»: añade el tema a equipo/busqueda_imagenes.json y haz push; resultados en equipo/imagenes_candidatas/ y hoja de contactos en la release pruebas).
   Prueba de comparación: ponerlo al lado de 2-3 reels reales del nicho que funcionaron (Buzzfy). Si se nota cuál es el nuestro por lo artificial, no sale.
6. Falta la línea "Fuentes:" en el texto, o el texto promete algo que el vídeo no cumple (cebo engañoso).

## Puntuación (100 puntos; mínimo 75 para publicar)
**Gancho, primeros 3 s (25)**
- Se entiende sin sonido y en menos de 2 s (máx. 10 palabras), con el texto ENTERO legible desde el primer fotograma o escrito en ≤ 0,5 s; mejor año + lugar/persona + acción (8).
- Abre una pregunta que solo se responde al final (hueco de curiosidad) (8).
- Hay movimiento o un elemento llamativo desde el primer fotograma, sin entradas lentas (5).
- La voz empieza en el primer segundo (4).

**Retención (25)**
- Duración de 20 a 35 s; más larga solo si cada escena aporta (5).
- Cambio visual cada 2-4 s (5).
- Cada escena añade un dato nuevo, sin relleno ni repeticiones, y al menos 3 escenas llevan una prueba visual propia (mapa, línea de tiempo, contador) y no solo decoración (8).
- Giro o revelación en el último tercio, con un final que invite a verlo otra vez (7).

**Ganas de compartir y guardar (20)**
- Provoca "no me lo creo, mira esto": el dato central sorprende de verdad (10).
- CTA concreto y en este orden: 1.º "Envíaselo a quien...", 2.º "Guárdalo", 3.º "Comenta 'PALABRA'" (5).
- Una razón para guardarlo: tarjeta final de recapitulación de 3 datos, lista numerada o Parte 2 (5).

**Exactitud y confianza (15)**
- Datos con matices cuando las fuentes difieren ("entre X e Y", "según las crónicas") (8).
- Fuentes nombradas en el texto (7).

**Texto del post y descubrimiento (15)**
- La primera línea repite el gancho con palabras clave buscables: nombre del caso, lugar, año (5).
- 4-6 líneas útiles, sin relleno; 4-6 hashtags de nicho (5).
- Portada (portada_ms) en un fotograma con el texto del gancho completo y legible (5).

## Reglas para remasters (añadido en v2)
- Antes de renderizar un remaster, el Remasterizador descarga el original y mira 4-6 fotogramas del tramo de recorte. Si hay marcas de agua, subtítulos quemados, pegatinas o imágenes que no encajan con el dato (p. ej. un retrato equivocado), NO se reutiliza ese metraje: el expediente se hace como reel nuevo con guion.json (escenas generadas por hacer_reel.py), conservando el formato ¿REAL O FALSO?.
- Solo se aprueba un remaster si el tramo recortado está limpio de marcas ajenas en todos los fotogramas.
- Los remasters aún sin renderizar del plan (17/11 koala de Queensland, 20/11 Limenocaris) deben pasar esta comprobación antes de renderizarse.

## Reglas de formato
- 1080x1920, H.264 + AAC, menos de 100 MB. Pico de audio por debajo de -1 dBFS; voz claramente por encima de la música.
- Texto clave entre y=500 e y=1450. Nada importante en los 350 px de abajo ni en los 150 de arriba.
- Números escritos con letra en la voz (la lectura sintética los pronuncia mejor).

## Registro de cambios
- v4.1, 6/11/2026 (19:40): el bloqueo 7a incluye las escenas que salen en negro porque una foto no se descargó en Actions (002 y 010 en el render de las 15:00 UTC) y la revisión mira un fotograma cada 2 s, no solo 6-8 repartidos. Un render caducado (el guion o la voz cambian y se vuelve a renderizar) invalida cualquier aprobación o rechazo previo.
- v1, 5/11/2026: versión inicial.
- v2, 6/11/2026: bloqueo explícito de marcas de agua ajenas en remasters y reglas de comprobación previa. Motivo: los remasters 003 (Koala Coyote) y 005 (oxígeno) mostraban iStock, Storyblocks, InVideo y «Grandes Misterios»; ambos fueron a revision/. Fuente: revisión de fotogramas de Calidad el 6/11/2026.
- v4, 6/11/2026 (13:10): bloqueo 7, «artificial o de plantilla», por orden del usuario (ningún reel ha funcionado). Evidencia: en Buzzfy (búsqueda de reels en español del nicho, 6/11) lo que llega a miles de visualizaciones con cuentas de ~1.000 seguidores es voz en off con vídeo o fotos reales y apertura de historia contada («Un tipo se puso a remodelar su casa, tumbó una pared y encontró una ciudad entera bajo tierra», 1.890 visualizaciones; Satoshi, 2.284 y 14 compartidos), mientras que una cuenta de estética «archivo clasificado» con rótulos tipo «MESA SERVIDA» se queda en 17-352. Toda la cola del 6/11 (002, 004, 010, 011) fue a revision/ por esto.
- v3, 6/11/2026: criterios basados en los modelos ganadores del nicho (equipo/modelos_ganadores.md): gancho legible desde el primer fotograma, prueba visual propia, orden de CTA (compartir, guardar, comentar) y tarjeta final guardable. Fuentes: informe de nicho de Buzzfy «Education & history», búsqueda de reels en español y Viral Reels Playbook 2026.
