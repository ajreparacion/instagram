# Modelos ganadores y cómo mejorarlos (Calidad, 6/11/2026)

Regla de oro: se copian ESTRUCTURAS (tipo de gancho, ritmo, longitud, recursos visuales, tipo de CTA), nunca contenido: ni vídeos, ni imágenes, ni guiones, ni frases literales de otras cuentas. Todo lo nuestro es original y con fuentes.

Fuentes de este análisis (solo patrones): informe de nicho «Education & history» de Buzzfy (140 reels, actualizado el 8/10/2026), búsqueda de reels en español con buen gancho y más de 20.000 visualizaciones (Buzzfy, 6/11/2026), Viral Reels Playbook 2026 de Buzzfy (aperturas y compartidos/guardados) y el ig_reel_checkup de la propia cuenta.

## Qué hacen los reels que funcionan (nicho historia/curiosidades)
1. Gancho de historia concreta: «Un soldado estadounidense enciende la radio en Vietnam, 1970» (6,5 M de reproducciones, cuenta verificada, 20 s); «En 2017, un ingeniero escribió una orden para borrar una carpeta» (3.355 visualizaciones, cuenta de 10 seguidores, 55 s). Fórmula: año + persona/lugar + acción, el texto escrito ya en el primer fotograma. Los ganchos story_open tienen la mediana más alta (558.000 reproducciones frente a 224.000 de «¿sabías que…?»).
2. «¿Sabías que…?» / secreto curioso es lo más repetido (28-34 % de los reels) y funciona en cuentas pequeñas (mediana 405.000-494.000), pero es lo que más copia todo el mundo. Mejor mezclarlo con historia concreta.
3. Imagen que prueba el dato: casi todos los grandes usan mapas animados, líneas de tiempo, líneas rectas entre lugares, contadores y fotos de archivo. El nº 1 del nicho (41 M) es un mapa animado de 6 s; otros: mapa de la guerra de Corea, expansión de EE. UU., línea recta de un templo al Polo Sur. Nuestros reels usan decoración genérica (silueta, radar, sello), que no demuestra nada.
4. Duración: menos de 20 s es la mejor banda en general; 20-45 s en cuentas verificadas; 45-75 s en pequeñas. Primer corte visual entre los 4,6 y 7,5 s; los ritmos son calmados (0,03-0,06 cortes por segundo) y la retención la sostiene la voz, no el montaje.
5. CTA: el 85 % de los reels no pide nada y su mediana es la más alta (388.000 frente a 49.600 de «sígueme»). Solo el 0,7 % usa «comenta PALABRA». El playbook mide: «guárdalo» 1,16 veces lo normal, «sígueme» 1,12, «envíaselo» 1,10, «comenta abajo» y «enlace en la bio» no suman nada.
6. Texto del post: 221 caracteres de mediana en el nicho; el playbook mide 5,0 guardados por cada 100 likes con pies de 700 o más caracteres frente a 1,9 con menos de 100. Los nuestros (600-700) están bien; el detalle útil y fechas ayudan a guardar.
7. Compartir: lo que se reenvía es «no te lo vas a creer». Los reels de archivo/nostalgia en español de cuentas pequeñas llegan a 1.000-1.300 compartidos con 100.000-200.000 visualizaciones. La actualidad (aniversarios: «hoy hace 154 años») ayuda.

## Dónde nos quedamos cortos (datos de la cuenta)
- 001 BAILE: salto 57 %, 0,14 veces lo normal; el playbook da un 2 % de probabilidad de despegue con ese salto. Meta: salto < 45 %.
- El gancho escrito aparece letra a letra y en el primer fotograma solo se lee «UN BARCO INT» / «EN 1932,» / «¿REAL O»: en los 2 primeros segundos hay que poder leerlo entero.
- Las escenas son decoración repetida (silueta de evidencia, radar verde): nada nuevo que ver entre dato y dato.
- No hay un recurso «guardable» (recapitulación, lista numerada, línea de tiempo) al final.

## Mejoras concretas (nuestra versión mejorada)
1. Gancho = año + lugar/persona + acción, ≤ 10 palabras, entero y legible desde el primer fotograma (o escrito en ≤ 0,5 s). Dejar la pregunta abierta.
2. Un recurso visual que PRUEBE el dato en al menos 3 de las 5-7 escenas, hecho por nosotros (original): mapa con la ruta o el lugar (Campion, Nueva York → Azores), línea de tiempo con las fechas, contador animado de cifras (20.000 emús → 986 abatidos → 57.034 recompensas), comparativa «dicen / dato». Fuentes de mapas: solo datos de dominio público (p. ej. Natural Earth), dibujados por código. Cualquier imagen de archivo solo si es de dominio público verificado (CC0 o anterior a 1900) con la fuente en el texto; si hay duda, no.
3. Cierre con tarjeta guardable: recapitulación de 3 datos (captura de pantalla) y orden de CTA: 1.º «Envíaselo a quien…», 2.º «Guárdalo», 3.º «Comenta PALABRA» (la palabra se mantiene porque dispara la respuesta automática y mide interés, pero no es lo que mueve el alcance).
4. Variedad de gancho: alternar historia concreta (año + persona) con «número + cosa imposible» (lista) para medir cuál rinde más con nuestra audiencia (España y Latinoamérica, 25-54 años).
5. Ritmo: primer cambio visual antes de los 5 s, giro antes del segundo 15 en los largos (pauta del Analista), y versión corta (< 25 s) siempre que el dato lo permita.
6. Reels de animales/naturaleza (el koala coyote original fue 5,95 veces lo normal): mantener 1 de cada 3.
7. Cada remaster ¿REAL O FALSO?: sin metraje antiguo (marcas de agua ajenas); reel nuevo de 20-25 s con el «real/falso» como gancho y mapa o contador como prueba.

## Peticiones a otros roles
- Mejora: en hacer_reel.py, mostrar el gancho completo en el primer fotograma (o ≤ 0,5 s de escritura; hoy va a nchars/1,1 s) y añadir un estilo «mapa/línea de tiempo/contador» y una tarjeta final de recapitulación.
- Creador: orden de CTA y recapitulación final (ver estandar_calidad.md v3).
- Estratega: medir en 2 semanas gancho de historia vs. «¿sabías que…?» y CTA «envíaselo/guárdalo» vs. «comenta»; decidir con compartidos por 100 likes y salto.
