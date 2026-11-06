# Instrucciones comunes del equipo de @nosabesloquehasvisto

Lee esto entero antes de tu rol (equipo/roles/<tu_rol>.md).

## DIRECTIVA VIGENTE (orden del usuario, 6/11/2026 20:27): IA FÁCIL PARA GENTE NORMAL
Sustituye por completo a «HUMANIZAR AL MÁXIMO» y al enfoque de misterios. Manda sobre cualquier otra regla de este archivo, del estándar de calidad y de los roles.
- Temática: IA y automatizaciones a nivel fácil para gente normal: sacar más partido a Claude, ChatGPT y Gemini, y trucos que hacen la vida más fácil (correo, trabajo, estudios, casa, móvil, automatizaciones gratis). Se acabaron los misterios y la serie ¿REAL O FALSO? (todo lo que había sin publicar está en descartados/).
- Formato: dibujos animados en movimiento estilo muñeco de palo / pizarra (doodle), hechos por código con herramientas/hacer_reel.py en "modo":"dibujo" (lo implementa Mejora de producción; ver «Modo dibujo» más abajo). Mascota fija: «Bit», robotito redondo blanco con pantalla-cara cian, que le enseña el truco a «Paco», muñeco de palo que se agobia con la tecnología. Fondo papel claro, trazo negro grueso, un solo color de acento cian. ChatGPT, Claude o Gemini pueden salir como personajes inventados con su nombre en texto, nunca con sus logos ni capturas con marca.
- Reel vertical de 20-35 s. Primeros 2 s: gancho de pregunta («¿Sabías que Gmail…?»), número («3 trucos…») o mini historia / antes-después («Paco tardaba una hora en…»); es lo que mejor funciona en cuentas pequeñas según el informe Buzzfy «AI & tech» de 6/11. Un truco o una lista de máx. 3, paso a paso, comprobado en la documentación oficial actual (centro de ayuda de OpenAI, Anthropic, Google, Apple, Microsoft…): nunca inventes funciones, precios ni nombres de menús; si una función depende del plan, del país o del idioma, se dice («en la versión gratis», «si te aparece»).
- Cierre: «Sígueme para un truco al día» o palabra clave en comentarios que envía por DM la guía o el prompt (campo "respuesta" de post.json, que lleva el prompt o los pasos de verdad, no un «te lo mando luego»).
- Voz cercana de España, como explicándoselo a un amigo, con las marcas de énfasis *así* (ver «ÉNFASIS»). Frases cortas, sin muletillas de IA («sumérgete», «descubre», «en este vídeo», «revoluciona»), máx. 2 emojis en el post. La voz sintética se sigue declarando en el texto del post («Voz: narración generada») mientras no sea la del dueño.
- Monetización (objetivo principal): alcance a no seguidores (reels de prueba, "prueba_no_seguidores"), palabra clave → DM, enlaces de afiliado solo de herramientas con programa oficial y avisando «enlace de afiliado», promoción de las apps de Neogest Lab cuando encaje (solo funciones reales comprobadas en la app), y preparar la publicación cruzada en YouTube Shorts (mismo vídeo 1080x1920 < 60 s).

## Contexto
- Cuenta de Instagram @nosabesloquehasvisto (nombre visible propuesto «IA Fácil · Trucos que no sabías», ver equipo/perfil_propuesto.md). Dueño: el usuario (Neogest Lab). Ha dado control total y autorización para trabajar de forma 100 % autónoma. OBJETIVO PRINCIPAL: MONETIZAR. El crecimiento y la viralidad son el medio. El usuario ha dado control y permisos absolutos.
- Regla de prioridad para todos los agentes: antes de decidir, lee equipo/monetizacion.md y elige siempre la opción que más acerque a ingresos reales (requisitos de monetización de Instagram, seguidores, alcance a no seguidores, retención, compartidos y guardados, temas con mayor valor comercial). Si dos opciones empatan, gana la que más monetiza. Nunca uses tácticas que pongan en riesgo la cuenta (spam, compra de seguidores, contenido engañoso o copiado).
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
"prueba_no_seguidores" (opcional): se publica como reel de prueba (trial reel) que Instagram enseña primero solo a no seguidores y que pasa al perfil si rinde. Por defecto en los reels de las 13:40 del plan; si la API lo rechaza, sale como reel normal.
NNN = siguiente número de 3 cifras tras los usados en cola/, publicados/, revision/, errores/ y descartados/.

## Formato de guion.json (reel nuevo; lo renderiza herramientas/hacer_reel.py)
{"titulo":"Truco NNN: ...","semilla":<entero>,"musica":true,"portada_texto":"...",
 "escenas":[{"texto":"frase corta en pantalla (máx. ~9 palabras)","duracion":3.5,"estilo":"gancho|archivo|evidencia|giro|cierre","voz":"lo que lee el narrador; números con letra"}]}
Opcional en cualquier escena: "sello":"FALSO" (o "REAL", "MITO", "CONFIRMADO"...) hace caer un sello grande de veredicto con golpe de sonido (rojo si es falso, verde si es real), a los 0,5 s en el giro o en "sello_t" segundos. Pensado para el ¿REAL O FALSO? hecho con guion.json: ponlo en la escena que da el veredicto.
Opcional en cualquier escena, para que la imagen PRUEBE el dato (sustituye al dibujo decorativo; uno por escena):
- "cifra":"20.000" (+ "unidad":"emús"): contador animado de 0 a la cifra en 1,3 s.
- "fechas":[{"anio":"1872","texto":"zarpa"}, ...] (2-4 hitos, texto ≤ 20 caracteres): línea de tiempo que se va llenando.
- "lista":["dato 1","dato 2","dato 3"] (máx. 3, ≤ 2 líneas cada uno): lista numerada que aparece punto a punto; úsala en el cierre como recapitulación guardable.

### Modo "dibujo" (OBLIGATORIO para reels nuevos desde el 6/11/2026 20:27; lo implementa Mejora)
Dibujos animados doodle sobre papel claro, trazo negro grueso y un único acento cian (#00B8D9 o similar). Sin fotos, sin vídeo real, sin logos de marcas. Subtítulos palabra a palabra como en el modo humano (texto = la propia "voz", énfasis en cian en vez de rojo) y voz de equipo/voz.json.
{"titulo":"Truco NNN: ...","semilla":<entero>,"modo":"dibujo","musica":true,"portada_texto":"gancho de máx. 7 palabras",
 "escenas":[{"estilo":"gancho|problema|paso|resultado|cierre","duracion":3.0,"voz":"lo que digo, con *énfasis*",
   "texto":"(opcional) rótulo corto arriba, p. ej. «PASO 1»",
   "dibujo":{"personajes":["paco","bit"],"accion":"agobiado|explica|senala|piensa|sorprendido|celebra",
             "objeto":"movil|portatil|correo|calendario|lista|reloj|bombilla|chat|carpeta|nada",
             "pantalla":["texto que se escribe dentro del móvil/portátil/chat, p. ej. el prompt", "máx. 3 líneas cortas"],
             "invitados":["chatgpt"|"claude"|"gemini"]}}]}
- Personajes: "paco" (muñeco de palo) y "bit" (robot redondo blanco, cara-pantalla cian, ojos que parpadean). "invitados" dibuja un personaje genérico inventado con una etiqueta de texto con su nombre (nunca su logo). El trazo se dibuja solo (efecto pizarra) y los personajes se mueven siempre algo (respiración, brazos, parpadeo): nada estático más de 1 s.
- "pantalla": el texto aparece letra a letra como si se tecleara; es lo que hace guardable el reel (el prompt o el menú exacto, comprobado en la documentación oficial).
- Siguen valiendo "cifra", "lista" (recapitulación final de máx. 3 pasos) y "sello" (p. ej. "GRATIS", "HECHO").
- Hasta que Mejora lo tenga en hacer_reel.py, el Creador escribe ya los guiones en este formato y GitHub no debe publicar uno con "modo":"dibujo" renderizado en otro modo (Mejora: que el render se salte el reel si no conoce el modo).

### Modo "humano" (EN DESUSO desde el 6/11/2026 20:27; se conserva la documentación para el énfasis y los subtítulos)
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

## Formato de remaster.json (EN PAUSA: los reels antiguos son de misterio/ficción y no encajan con la temática)
{"semilla":<entero>,"gancho":{"texto":"...","voz":"...","duracion":2.5},"recorte":{"inicio":s,"fin":s},
 "rotulos":[{"inicio":s,"fin":s,"texto":"..."}],"cierre":{"texto":"...","voz":"...","duracion":6.0},"musica":true,"volumen_original":0.8}

## Reglas de contenido (siempre)
- Cada truco, menú, precio o requisito se comprueba en la documentación oficial actual (y, si se puede, en una segunda fuente reciente); las URL van en "_fuentes" de post.json y en el texto una línea «Comprobado en: ayuda oficial de X (mes/año)». Nunca inventes funciones, nombres de menús, precios, cifras ni citas. Si algo solo existe en un plan de pago, en otro país o en inglés, se dice.
- Nada de consejos médicos, legales ni financieros personalizados; nada de trucos para saltarse normas, términos de uso, pagos o privacidad de otros; nada de pedir contraseñas ni datos personales. Siempre un aviso breve cuando el truco implique dar datos a una IA («no le pegues datos sensibles»).
- Sin logos ni capturas de marcas, sin vídeo, música ni imágenes de terceros. Afiliados solo con programa oficial y con «enlace de afiliado» en el texto.
- Cumple equipo/estandar_calidad.md.
