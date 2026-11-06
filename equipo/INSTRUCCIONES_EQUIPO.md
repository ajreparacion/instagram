# Instrucciones comunes del equipo de @nosabesloquehasvisto

Lee esto entero antes de tu rol (equipo/roles/<tu_rol>.md).

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

## Formato de remaster.json (reel antiguo; lo renderiza herramientas/remaster.py descargando el original_id)
{"semilla":<entero>,"gancho":{"texto":"...","voz":"...","duracion":2.5},"recorte":{"inicio":s,"fin":s},
 "rotulos":[{"inicio":s,"fin":s,"texto":"..."}],"cierre":{"texto":"...","voz":"...","duracion":6.0},"musica":true,"volumen_original":0.8}

## Reglas de contenido (siempre)
- Datos reales verificados con al menos 2 fuentes fiables; si difieren, se dice. Línea "Fuentes:" en el texto del post. Nunca inventes cifras, fechas, nombres ni citas.
- Nada de consejos de salud, tragedias recientes con víctimas, acusaciones a personas reales vivas ni desinformación. Nada de contenido ajeno (vídeos, música, imágenes de terceros).
- Cumple equipo/estandar_calidad.md.
