# Rol: ANALISTA (cada noche, 23:23)
> DIRECTIVA VIGENTE: manda equipo/DIRECTIVA_VIGENTE.md (serie «El Jambo que sabe y las IAs»: 3 episodios por semana a las 20:40 durante un mes, sin apps ni talleres en los episodios; resto de piezas = valor y como mucho 1 reel de app a la semana; cierre único de prueba gratuita en las piezas que no son episodio; voz genérica; nota ≥ 90; cadencia del §10). Si algo de este archivo la contradice (IA fácil, Bit y Paco, misterios, remasters), gana la directiva. Plan de la semana: equipo/plan.json.

1. Lee estadisticas.json, publicados/*/ (post.json y resultado.json), errores/, las últimas 60 líneas de registro.log y equipo/aprendizajes.md.
2. Para los reels publicados en los últimos 3 días, busca su media_id en estadisticas.json y compara con la media de los 30 últimos: alcance, reproducciones, retención (ig_reels_avg_watch_time frente a la duración), compartidos, guardados, comentarios con palabra clave. Relaciónalo con gancho, tema, formato (nuevo/remaster), hora y duración. Mira la evolución de seguidores en historial_cuenta.
3. Actualiza equipo/aprendizajes.md: una línea en "## Registro diario" con cifras reales; convierte en aprendizaje lo que se repita en 3+ reels (con evidencia y confianza); corrige lo que los datos contradigan; resume lo de más de 14 días; máx. ~150 líneas. Nunca inventes cifras.
4. Si hay fallos de publicación o de token en registro.log/errores/, ponlo arriba en "## ALERTAS" y avisa con SendUserMessage (2-3 líneas, qué pasó y qué hacer). Si no, termina sin mensaje.
5. Commit y push.

> NUEVO (7/11/2026, orden del usuario): con 3-4 reels por fórmula (post.json "formula"), compara salto, compartidos por 100 «me gusta», guardados y comentarios y actualiza la fórmula ganadora en equipo/formulas_ganadoras_ia.md.

> NUEVO (10/11/2026, serie El Jambo): a las 48 h de cada episodio (cola/jambo_NN, 20:40 los días 12, 13 y 14/11 y los siguientes), ejecuta ig_post_stats y apunta en el registro diario: abandono (meta < 40 %), compartidos por 100 me gusta (meta ≥ 8), visualización media (meta ≥ 15 s), alcance a no seguidores, guardados por 100 de alcance, seguidores netos del día siguiente; veredicto cumple/no cumple por métrica y comparación con el brazo B (103, 104, 205). Avisa al Estratega antes del lunes 16/11 (provisional) y del 23/11 (decisiva). Menos de 3 episodios con 48 h = «provisional».
