# Bucle de aprendizaje del equipo (vigente desde el 11/11/2026, orden del dueño: «ser el mejor equipo o desaparecer»)

Principio: **un error se paga una sola vez.** Cada rechazo de Calidad, cada dato del Analista y cada fallo del ciclo termina como una comprobación automática o una regla corta, no como un párrafo que nadie vuelve a leer.

## Al empezar (todos los roles, 1 minuto, solo lo necesario)
1. `python3 herramientas/pre_entrega.py --stats` (gratis, sin red): lista errores de las piezas de `cola/` y regenera `equipo/lecciones_calidad.md` (tasa de aprobación a la primera, motivos de rechazo más repetidos).
2. Lee solo `equipo/lecciones_calidad.md` y las 10 últimas líneas de `equipo/lecciones.md`. El resto de `aprendizajes.md` (38 KB) es archivo: se consulta con búsqueda, no se lee entero.

## Antes de entregar (Creador, Mejora, Estratega)
- `python3 herramientas/pre_entrega.py cola/<tu_carpeta>` debe terminar sin ERRORES. Los AVISOS se justifican en el commit o se corrigen. Comprueba: B9 (marcas de `equipo/marcas_prohibidas.json`), B6 (cierres «comenta/escríbeme X»), B8 (comentario fijado y avance), B1 (gancho ≤ 8 palabras), voz del dueño, primera línea repetida, reels a la misma hora y, desde el 14/11, la lista del 13/11 (≤ 20 s, reenvío, sin enlace ni venta en el reel, `marca_serie`, APP/WEB en el comentario fijado, personaje en el segundo 0).
- Calidad no gasta una pasada en lo que el revisor ya habría cogido: si una pieza llega con ERROR, vuelve sin puntuar.

## Al terminar (todos los roles, 1 línea)
Añade a `equipo/lecciones.md` una línea con este formato (una sola, la más útil de la ejecución):
`AAAA-MM-DD · ROL · qué pasó (dato) → regla nueva → cómo se comprueba (script, campo o fecha de revisión)`
- Si la regla se puede comprobar con código, **hazla comprobación** en `pre_entrega.py` o `marcas_prohibidas.json` en la misma ejecución (el rol Mejora lo hace si el rol que la descubre no puede).
- Una lección sin «cómo se comprueba» no se escribe.

## Cada lunes (Analista, junto a la lectura de datos)
1. Revisa `lecciones.md`: promueve a `estandar_calidad.md` las reglas que se cumplieron y mejoraron la nota o el alcance; borra las que los datos refutaron (con la cifra).
2. Compara con la semana anterior: tasa de aprobación a la primera, nota media, abandono, visualización media, alcance a no seguidores. Si una métrica empeora, el Estratega la convierte en prioridad de la semana y lo anota en `plan.json`.
3. Archiva lo viejo: lo anterior a 14 días de `aprendizajes.md` pasa a `equipo/archivo/` para que el fichero activo no crezca.

## Métricas del equipo (meta)
| Métrica | Hoy (11/11) | Meta |
|---|---|---|
| Aprobadas a la primera por Calidad | 62 % (31/50) | ≥ 85 % |
| Nota media de Calidad | 87,3 | ≥ 92 |
| Rechazos por cierre antiguo o marca ajena | 17 de 19 | 0 |
| Reels en la misma hora | 8 pares | 0 |
Fuente: `equipo/lecciones_calidad.md` (se regenera solo con `--stats`).

## Monetización obsesiva (11/11/2026)
Cada ejecución termina con una línea `MONETIZACIÓN: …` en `lecciones.md` (qué se hizo hoy que acerque el primer euro y qué paso del embudo mueve). El cuadro del día es `equipo/embudo.md`. Meta de la semana: la primera solicitud registrada en `equipo/leads.json`; después, conversión visita → clic ≥ 25 % y clic → solicitud ≥ 20 %.
