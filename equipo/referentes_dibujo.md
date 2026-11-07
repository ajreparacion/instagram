# Referentes del modo dibujo (explicadores animados / doodle de IA y tecnología)

Lo escribe Mejora de producción. Solo PATRONES MEDIBLES del sistema (estructura, ritmo, técnicas); nunca se copian dibujos, personajes, textos ni audio ajenos. Se revisa **1 vez por semana** (próxima: a partir del 14/11/2026); no repitas las búsquedas ya anotadas.

## 7/11/2026 · primer estudio (Buzzfy + web)
Búsquedas hechas (no repetir): Buzzfy `buzzfy_reel_search` «animated explainer about AI tools, doodle whiteboard cartoon characters, ChatGPT tips» (en+es, ≥100k vistas, most_viewed) y «truco de inteligencia artificial explicado con animación…» (es, ≤60 s, ≥50k, voiceover/tutorial/slideshow); `buzzfy_playbook` length_and_pace; web: «whiteboard doodle animation explainer Instagram Reels AI tech» y «animated explainer shorts retention cuts per second captions hook». La biblioteca de Buzzfy tiene pocos doodle puros: los referentes de abajo son reels de IA/tecnología que funcionan (formato de voz en off / tutorial) y explicadores animados conocidos.

### Cuentas y reels de referencia (solo patrones; cifras públicas en el momento de la búsqueda)
| Cuenta (seguidores) | Reel | Vistas | Dur. | Lo medible |
|---|---|---|---|---|
| @ai.with.andrew (61k) | «google just CHANGED PRIVACY» | 159k, 3,4k compartidos | 39 s | Tutorial con voz en off; 1.ª frase de urgencia («esto acaba de pasar»); texto grande en pantalla desde el s. 0; CTA guardar/compartir |
| @aguyandhiscomputer (3k) | «Can others see what you type into ChatGPT?» | 151k, 2,4k compartidos | 153 s | Pregunta directa + respuesta en pantalla («YES»); pasos numerados; palabra clave en comentarios (VAULT) |
| @aguyandhiscomputer (3k) | «Claude is probably lying to you» | 118k, 1,6k comentarios | 55 s | Orden imperativa en la 1.ª frase; palabra clave «guide» |
| @unoptimized_irk (1,5k) | «AI at work is such a mind f*ck» | 406k, 9k compartidos | 27 s | Cuenta pequeña, 27 s, humor con mini historia de la semana (antes/después), cierre «sígueme» |
| @faconplay (4k) | «Las reuniones de trabajo últimamente» | 201k, 7,4k compartidos | 11 s | Español; 11 s; una sola idea repetida en bucle (muy compartible) |
| @howitworks_studio (9k) | «How did this robot duck learn to walk?» | 119k | 60 s | Explicador animado en voz en off: pregunta «¿cómo…?» + texto en mayúsculas en el s. 0 |
| @the.legendary.edition (94k) | personaje animado «cerebro» | 1,05M | 187 s | Personaje dibujado que habla a cámara; arranca con «¿Sabías que…?»; pregunta al final para comentarios |
| @headai (19k) | corto animado | 2,4M, 177k me gusta | 60 s | Animación pura; gancho de diálogo en 1 s; sin CTA (el cierre emocional lo comparte la gente) |
| @elproferomero (536k) | explicación con voz en off | 209k | 14 s | Español; voz en off sobre lo que se ve; rótulo en mayúsculas arriba |
| Explicadores animados conocidos (Kurzgesagt, TED-Ed, minutephysics y sus Shorts) | — | — | 30-60 s en Shorts | Pizarra/objetos que se dibujan mientras la voz explica; corte o cambio visual cada 2-4 s; personaje simple con gestos; subtítulos grandes; música de fondo discreta + efectos («pop», «whoosh», lápiz) en cada aparición |

### Patrones medibles extraídos (lo que replicamos)
- **Duración**: 15-30 s para consejos; 25-40 s para tutoriales (Opus: retención > 80 % en 15-30 s; Buzzfy: la duración casi no importa, el visionado completo sí: los reels vistos más del 100 % rompen 1 de cada 4). Recortar el 30-40 % de un borrador apenas pierde retención (Buzzfy).
- **Gancho**: afirmación o pregunta directa en los primeros 2 s (dev.to/ClipSpeed: +67 % de espectadores a los 30 s frente a una apertura suave); el 50-60 % de los abandonos ocurre en los primeros 3 s (Opus). Texto grande en pantalla en el s. 0 en todos los referentes.
- **Cortes / cambios visuales**: uno cada 2-4 s (Opus); en los animados, además, algo se está dibujando o moviendo SIEMPRE (nada quieto más de 1 s).
- **Movimiento de cámara**: zoom/paneo leve continuo + «punch-in» (acercamiento rápido del 3-5 %) en cada corte.
- **Tipos de animación**: personaje que habla con la boca sincronizada y gesticula; pizarra/texto que se dibuja trazo a trazo; objetos que entran con rebote; flechas que se trazan; contadores.
- **Subtítulos**: quemados, grandes, alto contraste, palabra a palabra o por frases cortas, en el tercio medio (Opus: +15-25 % de retención).
- **Audio**: voz en off continua (sin huecos > 1,5 s), música de fondo discreta que no tapa la voz, efectos de sonido sutiles en cada aparición (pop, whoosh, lápiz, teclas).
- **Guion**: 0-3 s gancho → desarrollo paso a paso (máx. 3 puntos) → cierre con palabra clave o «sígueme»; la recompensa (el último paso, el resultado) en el último segundo; terminar con una frase/imagen que enlace con el principio para que se repita (Buzzfy).
- **Sin «bridge language»**: más del 12 % de frases de transición («en este vídeo», «vamos a ver») empeora el rendimiento (dev.to).

Fuentes web: bytecap.io/research/youtube-shorts-retention-benchmarks · longstories.ai/blog/retention-benchmarks-animated-youtube-videos · air.io (motion graphics y retención) · dev.to/kyle_clipspeedai (10.000 clips) · opus.pro/blog/ideal-youtube-shorts-length-format-retention.

### Estado de nuestro motor frente a estos patrones (7/11/2026, tras el cambio 19)
Cumple: 1080x1920 a 30 fps, gancho con texto grande en el s. 0, corte por escena (2-5 s) con «pop»+whoosh y punch-in, cámara leve continua, personajes que respiran/parpadean/gesticulan y boca sincronizada con la envolvente real de la voz, pizarra trazo a trazo con sonido de lápiz, objetos con rebote y flotación, texto tecleado con teclas, contador con «ding», subtítulos palabra a palabra, música discreta tras la primera frase.
Pendiente: transición dibujada entre escenas (barrido de rotulador), voz distinta para Paco, comparar retención real (estadisticas.json) de los reels en dibujo cuando haya 3-4 publicados.
