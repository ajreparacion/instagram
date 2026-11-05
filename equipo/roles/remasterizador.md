# Rol: REMASTERIZADOR (martes y viernes, 10:37) — formato "¿REAL O FALSO?"
1. Lee equipo/plan.json (entrada de hoy "tipo":"remaster"), equipo/aprendizajes.md, equipo/estandar_calidad.md, originales/*.json y equipo/remasters_hechos.txt (puede no existir).
2. Elige el original: el del plan; si no existe o ya se usó, el no usado con más likes + comentarios. Si ninguno, termina.
3. Descarga el original para estudiarlo: el render final lo hace GitHub, pero tú necesitas verlo. Instagram da su vídeo con la API solo desde GitHub Actions; aquí mírate su caption y, si quieres fotogramas, usa el permalink de originales/<id>.json con WebFetch para entender el tema. Si no puedes ver el vídeo, diseña el remaster con tiempos prudentes (tramo de 0 a 12 s).
4. Investiga 2-3 datos REALES y sorprendentes del mismo tema (≥2 fuentes).
5. Crea cola/<NNN>_realofalso_<id>/ con remaster.json (gancho "¿REAL O FALSO? ...", tramo 8-20 s, 2-4 rótulos que creen duda, cierre "Era FALSO. Lo real: ..." con los datos reales en la voz) y post.json con "original_id", palabra_clave y respuesta, "cuando" hoy 13:40 (o la hora del plan). Texto: "¿Real o falso?" + revelación (era ficción de esta misma cuenta) + datos reales + "📩 Envíaselo a quien se lo creyó." + Fuentes + hashtags (#realofalso #misterio #curiosidades #datoscuriosos + tema).
6. Añade el id a equipo/remasters_hechos.txt. Commit y push.
7. SendUserMessage breve: reel antiguo usado (permalink), datos reales y hora.
