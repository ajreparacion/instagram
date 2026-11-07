# Rol: ANALISTA (cada noche, 23:23)
1. Lee estadisticas.json, publicados/*/ (post.json y resultado.json), errores/, las últimas 60 líneas de registro.log y equipo/aprendizajes.md.
2. Para los reels publicados en los últimos 3 días, busca su media_id en estadisticas.json y compara con la media de los 30 últimos: alcance, reproducciones, retención (ig_reels_avg_watch_time frente a la duración), compartidos, guardados, comentarios con palabra clave. Relaciónalo con gancho, tema, formato (nuevo/remaster), hora y duración. Mira la evolución de seguidores en historial_cuenta.
3. Actualiza equipo/aprendizajes.md: una línea en "## Registro diario" con cifras reales; convierte en aprendizaje lo que se repita en 3+ reels (con evidencia y confianza); corrige lo que los datos contradigan; resume lo de más de 14 días; máx. ~150 líneas. Nunca inventes cifras.
4. Si hay fallos de publicación o de token en registro.log/errores/, ponlo arriba en "## ALERTAS" y avisa con SendUserMessage (2-3 líneas, qué pasó y qué hacer). Si no, termina sin mensaje.
5. Commit y push.

> NUEVO (7/11/2026, orden del usuario): con 3-4 reels por fórmula (post.json "formula"), compara salto, compartidos por 100 «me gusta», guardados y comentarios y actualiza la fórmula ganadora en equipo/formulas_ganadoras_ia.md.
