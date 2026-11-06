# Cuadro de mando semanal · @nosabesloquehasvisto (Fase 0, 6-16/11/2026)

Lo mantiene el Analista. La tabla de abajo la genera `herramientas/kpi.py` (solo biblioteca estándar) desde `estadisticas.json`, `publicados/*/` y `equipo/kpi_buzzfy.json`; no se edita a mano.

Regenerar: `python3 herramientas/kpi.py --buzzfy equipo/kpi_buzzfy.json --escribir` (ventana por defecto 7 días; `--dias 14` para otra).

## Qué mide cada KPI y de dónde sale
| KPI | Objetivo Fase 0 (monetizacion.md §5 / plan Estratega 5/11) | Fuente y cálculo |
|---|---|---|
| Seguidores netos / día | ≥ 0 (dejar de perder; hoy -0,33 a -0,46/día). Fase 1: +5/día sostenidos | `estadisticas.json` → `historial_cuenta`: (último − primero de la ventana) ÷ días. Si hay `seguidores_netos_dia` en kpi_buzzfy.json (de `ig_follower_growth`, días cerrados), manda ese. |
| Alcance a no seguidores / reel | ≥ 150 por reel (mitad del alcance meta de 300); en 30 días solo 27 no seguidores alcanzados | Solo Buzzfy: `ig_account_stats` → `reach.nonFollowers` de la ventana ÷ reels publicados del enfoque nuevo. Por reel, `ig_post_stats` no lo desglosa; cuando Instagram lo dé, va en `no_seguidores_por_reel`. |
| Alcance / reel | Mediana ≥ 100 a 48 h en los 10 primeros reels (decisión del 16/11); meta por reel ≥ 300 | `posts[].metricas.reach` de los reels con `timestamp` ≥ 5/11/2026 20:00 UTC (enfoque nuevo) en la ventana. Referencia: mediana de los 30 últimos. |
| Compartidos / reel | ≥ 3 por reel (hoy 0; mediana histórica 0) | `posts[].metricas.shares`, media de la ventana. |
| Guardados / reel | ≥ 2 por reel (hoy 0) | `posts[].metricas.saved`, media de la ventana. |
| Clics en el enlace / semana | Enlace activo al hub (hoy la bio apunta a TikTok, 0 clics). Fase 1: 20/semana | Solo Buzzfy: `ig_account_stats` → `profileActivity.websiteClicks` + `linkTaps`. |
| Visualización media (s) | ≥ 15 s (histórico: 15-18 s ⇒ 849 reproducciones de mediana; < 8 s ⇒ 226) | `posts[].metricas.ig_reels_avg_watch_time` ÷ 1000, media de la ventana. |
| % visto | ≥ 50 % del reel (giro antes del segundo 15) | Visualización media ÷ duración. Duración: último `inicio + duracion` de `publicados/<reel>/locucion.json` (o suma de `escenas[].duracion` de guion.json). n/d si la carpeta no conserva esos archivos (caso del 001). |

Reglas: todo reel con < 48 h es PROVISIONAL (Instagram tarda hasta 48 h en asentar). No se comparan reels de prueba para no seguidores con reels normales en la misma fila sin indicarlo. Lectura semanal: domingo noche; decisión de Fase 0: 16/11 con 10 reels medidos a 48 h.

## Tabla (generada)
<!-- KPI:INICIO -->
Actualizado con estadisticas.json de 06/11/2026 15:02 UTC · ventana 7 días · 1 reel(s) del enfoque nuevo · PROVISIONAL: hay reels con < 48 h
Cifras de Buzzfy copiadas a mano el 2026-11-06 23:24 CET (ventana 7 días).

| KPI | Valor actual | Objetivo Fase 0 | Cómo se calcula |
|---|---|---|---|
| Seguidores netos / día | -0,33 | ≥ 0 (dejar de perder); Fase 1: +5/día | historial_cuenta: Buzzfy ig_follower_growth (2026-11-06 23:24 CET) |
| Alcance a no seguidores / reel | 15,0 | ≥ 150 (la mitad de los 300 de alcance meta por reel) | solo Buzzfy (ig_account_stats reach.nonFollowers ÷ reels de la ventana); n/d si no se pasa --buzzfy |
| Alcance / reel (media · mediana) | 21,0 | mediana ≥ 100 a 48 h en los 10 reels (decisión del 16/11); meta ≥ 300 | metricas.reach; mediana ventana 21; referencia 30 últimos 130,0 |
| Compartidos / reel | 0,00 | ≥ 3 por reel | metricas.shares; referencia 30 últimos (mediana) 0,0 |
| Guardados / reel | 0,00 | ≥ 2 por reel | metricas.saved; referencia 30 últimos (mediana) 0,0 |
| Clics en el enlace / semana | 0 | enlace activo al hub; Fase 1: 20/semana | solo Buzzfy (ig_account_stats profileActivity.websiteClicks + linkTaps) |
| Visualización media (s) | 14,4 | ≥ 15 s | ig_reels_avg_watch_time ÷ 1000; referencia 30 últimos (mediana) 9,4 s |
| % visto (vis. media ÷ duración) | n/d | ≥ 50 % del reel | duración de publicados/*/locucion.json o guion.json; n/d si la carpeta no los conserva |

| Reel | Publicado (CET) | Edad | Alcance | Repr. | Comp. | Guard. | Coment. | Vis. media | Duración | % visto |
|---|---|---|---|---|---|---|---|---|---|---|
| 17996499894053316 | 05/11 21:46 | 18 h (prov.) | 21 | 28 | 0 | 0 | 0 | 14,4 s | n/d | n/d |

Referencia: mediana de los 30 reels de estadisticas.json — alcance 130,0, compartidos 0,0, guardados 0,0, visualización media 9,4 s.
<!-- KPI:FIN -->

## Histórico semanal (lo rellena el Analista cada domingo)
| Semana | Seg. netos/día | Alcance no seg./reel | Alcance/reel | Comp./reel | Guard./reel | Clics/sem | Vis. media | % visto | Nota |
|---|---|---|---|---|---|---|---|---|---|
| 30/10-6/11 (parcial, 1 reel) | -0,33 (23/10-3/11, Buzzfy) | 14 (cuenta a 7 días, 1 reel) | 16-21 (prov.) | 0 | 0 | 0 | 12,1-14,4 s (prov.) | n/d | Solo 001 BAILE; bio sin hub de enlaces |
