# Instrucciones comunes del equipo de @nosabesloquehasvisto

Lee esto entero antes de tu rol (equipo/roles/<tu_rol>.md).

## PRIORIDAD MÁXIMA (orden del usuario, 6/11/2026): HUMANIZAR AL MÁXIMO
Ningún reel ha funcionado hasta ahora. Nada debe parecer hecho por IA ni de plantilla. Esto manda sobre cualquier otra regla de estilo de este archivo, del estándar de calidad y de los roles:
- Guion en PRIMERA PERSONA, como alguien contándole algo a un amigo: frases cortas, coloquiales, de España («a ver», «ojo», «te juro que», «flipé»…), con dudas y reacciones propias («y aquí viene lo bueno»). Sin muletillas de IA («sumérgete», «descubre», «en este vídeo», «fascinante», «impactante»), sin voz de locutor ni de documental, sin exceso de emojis (máximo 2 en todo el texto del post).
- Voz lo más natural posible: ritmo variable, pausas de verdad (puntos, comas y puntos suspensivos en el campo "voz"), entonación de conversación, alguna frase que se corta o se repite como al hablar. Nunca una frase que un locutor leería de un papel.
- Imágenes y clips REALES en lugar de fondos generados: fotos y vídeos de dominio público o con licencia libre (Wikimedia Commons, archivos nacionales, NASA, Pexels/Pixabay con licencia libre), o vídeos propios del usuario (los reels de originales/ solo si el fotograma está limpio de marcas ajenas). Los fondos abstractos generados (ojos, polígonos, «REC», «CLASIFICADO») quedan prohibidos para reels nuevos: herramientas/hacer_reel.py los sustituye por el modo "humano" (ver Formato de guion.json).
- Movimiento de cámara leve (zoom y paneo lentos sobre cada foto), cortes rápidos (cambio de imagen cada 2-4 s), subtítulos estilo creador palabra a palabra (grandes, blancos, centrados, 2-4 palabras en pantalla, la actual resaltada), música discreta muy por debajo de la voz.
- Antes de dar un reel por bueno, compáralo con reels virales reales del nicho (Buzzfy buzzfy_reel_search / buzzfy_niche_report_reels o búsqueda web) y descarta o reescribe lo que suene o se vea artificial. Si dudas entre «correcto» y «humano», gana humano.
- Esta directiva se aplica también a los reels que ya están en cola/ sin publicar: quien los toque los reescribe y les quita "renderizado" y "asset" de post.json para que se vuelvan a renderizar.

## Contexto
- Cuenta de Instagram @nosabesloquehasvisto, nombre visible "Expedientes Imposibles 🔍". Dueño: el usuario (Neogest Lab). Ha dado control total y autorización para trabajar de forma 100 % autónoma. OBJETIVO PRINCIPAL: MONETIZAR. El crecimiento y la viralidad son el medio. El usuario ha dado control y permisos absolutos.
- Regla de prioridad para todos los agentes: antes de decidir, lee equipo/monetizacion.md y elige siempre la opción que más acerque a ingresos reales (requisitos de monetización de Instagram, seguidores, alcance a no seguidores, retención, compartidos y guardados, temas con mayor valor comercial). Si dos opciones empatan, gana la que más monetiza. Nunca uses tácticas que pongan en riesgo la cuenta (spam, compra de seguidores, contenido engañoso o copiado).
- Enfoque actual: MISTERIOS REALES y datos verdaderos que parecen inventados (serie EXPEDIENTES numerada, todo con fuentes). Martes y viernes: "¿REAL O FALSO?" reutilizando reels antiguos de ficción de la propia cuenta y desmontándolos con datos reales. El Estratega puede cambiar el enfoque si los datos lo justifican.
- Nada depende de ningún dispositivo del usuario: todo vive en el repositorio privado GitHub ajreparacion/instagram, y GitHub Actions (publicar_gh.py, cada 30 min de 12:05 a 23:35) renderiza, pone la voz, publica, responde comentarios y actualiza estadisticas.json.
- Escribe siempre en español de España. No hagas preguntas: decide tú y deja constancia.

## Cómo trabajar con el repositorio
1. Conecta el repo con la herramienta mcp__claude-code-remote__add_repo (owner "ajreparacion", repo "instagram", access "push") y clónalo como te indique su respuesta (git clone --depth 1 https://github.com/ajreparacion/instagram /home/claude/instagram).
2. Trabaja en /home/claude/instagram. Al terminar: git add -A; git commit -m "<rol>: <qué>"; git pull --rebase; git push. Si el push falla por conflicto, vuelve a hacer pull --rebase y push (máx. 3 intentos).
3. Nunca subas vídeos ni audios al historial de git (solo JSON, Markdown y scripts). Los vídeos renderizados están en la release "cola" del repo.
4. Para descargar un vídeo renderizado (asset "<carpeta>.mp4" de la release cola):
   ID=$(gh api repos/ajreparacion/instagram/releases/tags/cola --jq '.assets[] | select(.name=="NOMBRE.mp4") | .id')
   gh api -H "Accept: application/octet-stream" repos/ajreparacion/instagram/releases/assets/$ID > NOMBRE.mp4
5. No toques .github/ ni publicar_gh.py salvo el rol de Mejora (y solo con prueba previa). Nunca escribas tokens ni secretos en ningún archivo.

## Carpetas
- cola/<NNN_tema>/: post.json (+ guion.json para reel nuevo, o remaster.json para reutilizar uno antiguo), calidad.json (lo escribe Calidad), locucion.json (lo escribe el render).
- publicados/, revision/ (rechazados por Calidad), errores/, descartados/, originales/<id>.json (reels antiguos de la cuenta).
- equipo/: plan.json (Estratega), aprendizajes.md (Analista; decisiones vigentes), estandar_calidad.md (Calidad), monetizacion.md (Analista de monetización), mejoras.md y voz.json (Mejora), respondidos.json (automático).
- estadisticas.json: últimos 30 posts con métricas (reach, views, saved, shares, comments, likes, total_interactions, ig_reels_avg_watch_time en ms) y historial de seguidores.
- registro.log: lo que hace GitHub Actions (renders, publicaciones, errores).

## Formato de post.json
{"tipo":"reel","texto":"<texto del post>","cuando":"AAAA-MM-DDTHH:MM:00+01:00 (o +02:00 en verano)",
 "palabra_clave":"PALABRA del CTA","respuesta":"respuesta automática a quien comente la palabra (máx. 200 caracteres, sin enlaces)",
 "compartir_en_feed":true,"portada_ms":2800, "original_id":"<solo remaster: id del reel antiguo>",
 "prueba_no_seguidores":true}
"prueba_no_seguidores" (opcional): se publica como reel de prueba (trial reel) que Instagram enseña primero solo a no seguidores y que pasa al perfil si rinde. Por defecto en todos los remasters ¿REAL O FALSO?; si la API lo rechaza, sale como reel normal.
NNN = siguiente número de 3 cifras tras los usados en cola/, publicados/, revision/, errores/ y descartados/.

## Formato de guion.json (reel nuevo; lo renderiza herramientas/hacer_reel.py)
{"titulo":"Expediente NNN: ...","semilla":<entero>,"musica":true,"portada_texto":"...",
 "escenas":[{"texto":"frase corta en pantalla (máx. ~9 palabras)","duracion":3.5,"estilo":"gancho|archivo|evidencia|giro|cierre","voz":"lo que lee el narrador; números con letra"}]}
Opcional en cualquier escena: "sello":"FALSO" (o "REAL", "MITO", "CONFIRMADO"...) hace caer un sello grande de veredicto con golpe de sonido (rojo si es falso, verde si es real), a los 0,5 s en el giro o en "sello_t" segundos. Pensado para el ¿REAL O FALSO? hecho con guion.json: ponlo en la escena que da el veredicto.
Opcional en cualquier escena, para que la imagen PRUEBE el dato (sustituye al dibujo decorativo; uno por escena):
- "cifra":"20.000" (+ "unidad":"emús"): contador animado de 0 a la cifra en 1,3 s.
- "fechas":[{"anio":"1872","texto":"zarpa"}, ...] (2-4 hitos, texto ≤ 20 caracteres): línea de tiempo que se va llenando.
- "lista":["dato 1","dato 2","dato 3"] (máx. 3, ≤ 2 líneas cada uno): lista numerada que aparece punto a punto; úsala en el cierre como recapitulación guardable.

### Modo "humano" (obligatorio para reels nuevos desde el 6/11/2026)
Añade "modo":"humano" al guion. Entonces hacer_reel.py NO dibuja fondos generados ni HUD: cada escena lleva fotos reales con movimiento de cámara leve y subtítulos palabra a palabra sincronizados con la voz (estimada a ~2,6 palabras/s; el texto en pantalla es la propia "voz", así que "texto" solo hace falta en el gancho y en el cierre).
{"titulo":"...","semilla":<entero>,"modo":"humano","musica":true,"portada_texto":"gancho de máx. 8 palabras",
 "escenas":[{"estilo":"gancho|archivo|evidencia|giro|cierre","duracion":3.0,"voz":"lo que digo, coloquial, con pausas (comas, puntos, …)",
   "texto":"(opcional) rótulo corto fijo arriba, p. ej. «1932 · Australia»",
   "imagenes":[{"url":"https://upload.wikimedia.org/...","credito":"Autor · Dominio público","mov":"zoom_in|zoom_out|pan_izq|pan_der"}]}]}
- "imagenes": 1-3 por escena (corte cada 2-4 s). Solo dominio público o licencia libre (CC0, CC BY, CC BY-SA con crédito). El crédito se muestra pequeño en pantalla y la licencia debe anotarse en "_imagenes" de post.json. Si una URL falla al descargar, el render usa un fondo de textura neutra (no se cae), pero Calidad lo marca.
- ÉNFASIS (desde el 6/11/2026, orden del usuario «falta gancho y énfasis»): en "voz" (y en "texto" del gancho) marca entre asteriscos la palabra o las 2-3 palabras clave de la frase: `"voz": "Solo falta *una* cosa. *El bote salvavidas*."`. La voz las dice más fuerte (+3,5 dB) con un respiro antes, y en los subtítulos salen en ROJO. Úsalo en el gancho (1 marca), en el giro (1-2) y como mucho una vez más; sin marcas no hay énfasis. Los asteriscos no llegan al motor de voz. Además, el gancho y el giro se generan con más intensidad que el resto (equipo/voz.json → chatterbox.por_estilo) y la música no entra hasta que acaba la primera frase: la primera frase va a pelo, así que debe ser la más corta y la más fuerte del reel.
- CLIPS DE VÍDEO REAL (desde el 6/11/2026, prioritarios frente a las fotos cuando existan): una entrada de "imagenes" puede ser un vídeo en vez de una foto, con las mismas reglas de licencia y el mismo crédito:
  {"video":"https://upload.wikimedia.org/....webm","inicio":12.0,"credito":"Autor · Dominio público","mov":"zoom_in"} → URL directa de un vídeo (Commons .webm/.ogv/.mp4, NASA, Pexels/Pixabay con licencia libre) o ruta local relativa a la carpeta del reel.
  {"original_id":"18064409066120359","inicio":3.0,"credito":"Vídeo propio"} → un reel antiguo de la propia cuenta (id de originales/); publicar_gh.py lo descarga de la API al renderizar. Solo si el fotograma está limpio de marcas ajenas (iStock, Storyblocks, InVideo…).
  "inicio" = segundo del clip por el que empieza; el clip ocupa su tramo de la escena a velocidad real, sin su audio, y si es más corto que el tramo se repite en bucle. Los apaisados van sobre sí mismos desenfocados. "mov" solo zoom_in | zoom_out | fijo (sin paneo: el vídeo ya se mueve). Si el vídeo no se puede descargar o leer, la entrada se ignora y la escena sigue con sus fotos o el fondo neutro (queda anotado en registro.log).
- Caché local: las imágenes se descargan a ~/.cache/expedientes/imagenes/ (GitHub Actions las cachea con la voz).

## Formato de remaster.json (reel antiguo; lo renderiza herramientas/remaster.py descargando el original_id)
{"semilla":<entero>,"gancho":{"texto":"...","voz":"...","duracion":2.5},"recorte":{"inicio":s,"fin":s},
 "rotulos":[{"inicio":s,"fin":s,"texto":"..."}],"cierre":{"texto":"...","voz":"...","duracion":6.0},"musica":true,"volumen_original":0.8}

## Reglas de contenido (siempre)
- Datos reales verificados con al menos 2 fuentes fiables; si difieren, se dice. Línea "Fuentes:" en el texto del post. Nunca inventes cifras, fechas, nombres ni citas.
- Nada de consejos de salud, tragedias recientes con víctimas, acusaciones a personas reales vivas ni desinformación. Nada de contenido ajeno (vídeos, música, imágenes de terceros).
- Cumple equipo/estandar_calidad.md.
