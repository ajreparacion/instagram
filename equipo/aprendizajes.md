# Aprendizajes de @nosabesloquehasvisto

## ALERTAS
- Ninguna (5/11/2026 22:25): sin errores en registro.log ni en errores/. Ojo: cola/ está vacía tras publicar el 001; si nadie produce, mañana no se publica.

Archivo compartido del equipo. Lo actualiza el Analista cada noche. Lo leen el Estratega, el Creador y el Remasterizador antes de trabajar.
Regla: cada aprendizaje lleva evidencia y confianza (alta/media/baja). Sin evidencia es "hipótesis".

## Punto de partida (5/11/2026)
- Cuenta: 1.605 seguidores, 808 publicaciones. Interacción reciente muy baja: 1-18 likes y 0-2 comentarios por reel (últimos 30). Confianza: alta (datos de la API).
- Desde el 5/11/2026 21:30 hay métricas completas (alcance, reproducciones, guardados, compartidos, tiempo medio de visualización en ms). Ejemplo real: reel del koala (25/10/2026) alcance 30, 41 reproducciones, 2 compartidos, 11,5 s de visualización media; reel del 26/09/2025 alcance 209 pero solo 2,6 s de media (el gancho no retenía). Confianza: alta.
- Contenido histórico mezclado: podcast "Sara Empírica" (2024), "Sal Gurú" (2024), bestiario de criaturas inventadas y koalas (2025), sketches. Nicho poco definido. Confianza: alta.
- Publicación irregular: huecos de meses entre reels (sep 2025 → oct 2025 → nov 2026). Confianza: alta.
- Hipótesis: las series numeradas rinden algo mejor (la serie "Sara Empírica" de marzo-abril 2024 tuvo 8-18 likes, por encima de la media). Confianza: baja.
- Aprendizaje: el gancho "¿Y si...?" funcionó mejor que la media. Evidencia: 3 reels (aire 8/6/25, oxígeno 6/6/25, streamers 8/6/25) con alcance 182/158/211 (media 184 frente a mediana de 130 de los 30 últimos) y 3 de los 6 comentarios totales de los 30 últimos posts. Confianza: media.

## Referencias de los 30 últimos posts (estadisticas.json, 5/11/2026)
- Media / mediana: alcance 126,7 / 130; reproducciones 297,6 / 212,5; likes 6,4 / 5,5; guardados 0,4 / 0; compartidos 0,5 / 0; comentarios 0,2 / 0; visualización media 10,1 s / 9,4 s. Mediana de Buzzfy (19 reels): alcance 156, 8,4 s de visualización, 65 % de salto.
- Aprendizaje: guardados, compartidos y comentarios son casi nulos en todo el histórico (≤3 por reel en los 30). La meta realista a corto plazo es pasar de 0 a 2-5 compartidos por reel. Confianza: alta.
- Aprendizaje: el bestiario "Descubre el..." (6 reels, 28/5-5/6/25) rinde en la media (alcance 137-179) salvo un pico: Canis arboricola 1.013 de alcance y 16,2 s de visualización (el mejor de los 30). Un tema puede romper la media sin cambiar formato. Confianza: media.
- Aviso de datos: los reels de 2024 (Sara Empírica, Sal Gurú) muestran alcance 7-36 pero 150-1.317 reproducciones; el alcance antiguo de la API no es comparable. Compara 2024 solo por reproducciones y likes. Confianza: alta.
- Seguidores (Buzzfy, 22/10-2/11/2026): +6 / -11 = -5 netos en 12 días cerrados. La cuenta pierde seguidores lentamente sin publicar. Confianza: alta.

## Decisiones vigentes
- (Corregido 5/11/2026 por el Analista, según INSTRUCCIONES_EQUIPO.md) Enfoque vigente: MISTERIOS REALES con fuentes (serie EXPEDIENTES numerada) + martes y viernes "¿REAL O FALSO?" desmontando reels antiguos de ficción. Sustituye al antiguo "falso documental con humor". Lo puede cambiar el Estratega con datos.
- Ritmo: 1 reel nuevo al día + 2 remasterizaciones por semana. El primero (001) salió a las 21:46, no a las 20:40: la hora la fija el Estratega en plan.json.
- Si se reutiliza un reel de ficción, se deja claro que era ficción y se desmonta con datos reales (#documentalfalso solo para señalar la ficción original).
- 5/11/2026 ESTRATEGA: el nicho es MISTERIOS REALES y datos verdaderos que parecen inventados (serie EXPEDIENTES con fuentes) + ¿REAL O FALSO? martes y viernes con reels antiguos. Motivo: la ficción no tuvo tracción (1-11 likes, 0-2 comentarios) y el algoritmo de 2026 premia compartidos por DM y retención, que se ganan con "no me lo creo, pero es verdad".
- 5/11/2026 ESTRATEGA: se aprovechan aniversarios reales del mes (Emú 2/11/1932, Mary Celeste 7/11/1872, Manises 11/11/1979, viernes/martes 13) y se cumple siempre la Parte 2 prometida (la del 001 baile sale el 8/11). Motivo: las fechas dan gancho y actualidad; romper una promesa de Parte 2 resta confianza.
- 5/11/2026 ESTRATEGA: experimento de la semana = duración corta (20-25 s) frente a larga (36-42 s), campo "duracion_objetivo" en plan.json; métrica: % visto medio y alcance + compartidos a 48 h. Motivo: la retención es la señal principal y es medible con ig_reels_avg_watch_time.

- 5/11/2026 CALIDAD: antes de producir, Creador y Remasterizador leen equipo/estandar_calidad.md y lo cumplen. El agente de Calidad revisa cada reel de cola/ a las 12:31 y 19:31; lo que no pasa va a revision/ y no se publica.

- 5/11/2026 COMENTARIOS: todo post.json (nuevo o remaster) incluye además "palabra_clave" (la palabra del CTA, p. ej. "BAILE") y "respuesta" (texto corto y amable, máx. 200 caracteres, sin enlaces) que GitHub Actions enviará automáticamente como respuesta a cada comentario que contenga esa palabra, durante 7 días. Cuando se publique la Parte 2, la respuesta puede avisar de que ya está publicada.

## Registro diario
(El Analista añade aquí una línea por día: fecha, qué se publicó, resultado a 24-48 h, conclusión.)
- 5/11/2026 · 001 Epidemia de baile 1518 (reel nuevo, 21:46, CTA "BAILE"). A los 32-40 min: alcance 1-2, 6 reproducciones, 0 likes/guardados/compartidos/comentarios; visualización media 38,7 s (Actions) / 26,1 s (Buzzfy, provisional), unas 3 veces la mediana de la cuenta; salto 40 % (mediana 65 %). Seguidores 1.605. Conclusión: demasiado pronto para juzgar el alcance; la retención inicial es buena señal para el formato de misterio real. Reevaluar a 24-48 h.
