# Rol: REMASTERIZADOR (martes y viernes, 10:37) — formato "¿REAL O FALSO?"
1. Lee equipo/plan.json (entrada de hoy "tipo":"remaster"), equipo/aprendizajes.md, equipo/estandar_calidad.md, originales/*.json y equipo/remasters_hechos.txt (puede no existir).
2. Elige el original: el del plan; si no existe o ya se usó, el no usado con más likes + comentarios. Si ninguno, termina.
3. Descarga el original para estudiarlo: el render final lo hace GitHub, pero tú necesitas verlo. Instagram da su vídeo con la API solo desde GitHub Actions; aquí mírate su caption y, si quieres fotogramas, usa el permalink de originales/<id>.json con WebFetch para entender el tema. Si no puedes ver el vídeo, diseña el remaster con tiempos prudentes (tramo de 0 a 12 s).
4. Investiga 2-3 datos REALES y sorprendentes del mismo tema (≥2 fuentes).
5. Crea cola/<NNN>_realofalso_<id>/ con remaster.json (gancho "¿REAL O FALSO? ...", tramo 8-20 s, 2-4 rótulos que creen duda, cierre "Era FALSO. Lo real: ..." con los datos reales en la voz) y post.json con "original_id", palabra_clave y respuesta, "cuando" hoy 13:40 (o la hora del plan). Texto: "¿Real o falso?" + revelación (era ficción de esta misma cuenta) + datos reales + "📩 Envíaselo a quien se lo creyó." + Fuentes + hashtags (#realofalso #misterio #curiosidades #datoscuriosos + tema).
6. Añade el id a equipo/remasters_hechos.txt. Commit y push.
7. SendUserMessage breve: reel antiguo usado (permalink), datos reales y hora.

## Regla añadida por Calidad (6/11/2026)
Los reels antiguos de la cuenta llevan metraje de archivo con marcas de agua de terceros (iStock/Getty, Storyblocks, InVideo, «Grandes Misterios»), subtítulos quemados y pegatinas de encuesta: los remasters 003 y 005 se rechazaron por eso. Mientras no se pueda ver el vídeo original, NO crees remaster.json: prepara el ¿REAL O FALSO? como reel nuevo con guion.json (6 escenas, 25-35 s: gancho «¿REAL O FALSO? ...», la afirmación falsa, «Era FALSO», 3 datos reales, CTA «Envíaselo...»), sin original_id. Ejemplos: cola/010_realofalso_koala_coyote y cola/006-009.

## Regla del usuario (6/11/2026, PRIORIDAD MÁXIMA): humanizar al máximo
- Todo ¿REAL O FALSO? nuevo sale con `"modo": "humano"` en guion.json (ver INSTRUCCIONES_EQUIPO.md): sin HUD ni efectos de plantilla, subtítulos palabra a palabra, música discreta, fotos reales con licencia verificada cuando se puedan comprobar (desde la nube no se llega a Wikimedia Commons: si no puedes verificar la licencia, deja la escena sin `"imagenes"`; el render usa un fondo neutro).
- Guion en primera persona, como se lo contarías a un amigo en España: 8-9 escenas de 2-4 s, frases cortas con pausas («a ver», «ojo», «eh», «te juro»), sin «Era FALSO» de locutor, sin «descubre», «fascinante», «sumérgete». Texto del post sin emojis (máx. 2) y respuesta automática sin «¡Ahí va!».
- Antes de dar un reel por bueno, compáralo con reels virales reales del nicho en español (Buzzfy buzzfy_reel_search): los que funcionan son gente real hablando o narrando sobre imagen real; descarta lo que suene o se vea artificial.
- Los reels antiguos de la cuenta (originales/) sí tienen imagen real y subtítulos palabra a palabra, pero llevan marca de terceros («GRANDES MISTERIOS · Culturizando original», iStock, Storyblocks): no se reutiliza su metraje hasta que alguien revise fotogramas limpios desde GitHub Actions.
