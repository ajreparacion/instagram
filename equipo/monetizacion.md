# Monetización de @neogestlab (Neogest Lab · escaparate de apps y webs)

Analista de monetización. Versión 8: 13/11/2026 ~12:30 UTC (revisión diaria del embudo). Sustituye a la v7.1 del 12/11. Rige equipo/DIRECTIVA_VIGENTE.md (no se toca). Vías de Instagram y afiliados con fuentes: `monetizacion_v4_archivo.md`.
Regla: lo que no se ha leído en una fuente va como «no consta» o «n/d». Sin gasto ni promociones sin visto bueno del dueño.
Fuentes de hoy, solo lectura: Buzzfy (`ig_account_stats` y `ig_follower_growth`, 6-13/11) y Base44 del Centro (entidades `SolicitudInfo` y `Clic`). `equipo/embudo.md` se regeneró con `herramientas/embudo.py`, pero sus cifras son las del 12/11 15:42; las de esta versión son más recientes. Sin navegador comprobado en esta sesión.

## 0. Resumen ejecutivo
- **Embudo 6-13/11 (7 días):** 872 cuentas no seguidoras alcanzadas → **15 visitas al perfil (1,7 %; meta ≥ 3 %)** → **4 clics al sitio web (27 % de las visitas; meta ≥ 25 %)** → **0 solicitudes nuevas** → **0 €**.
- **El paso más débil sigue siendo alcance → visita al perfil.** Empeora frente al 5-12/11 (1,9 %), aunque sube el alcance (929 cuentas en total).
- **El dato que más cambia la lectura:** el 12/11 a las 19:55 se registra un clic de origen «bio» hacia `aj-reparacion-web` (Centro). Es el primero desde la bio con el enlace nuevo. No consta por qué ruta llegó, porque el enlace de la bio es `/solicitar?src=instagram`.
- **La solicitud del 8/11 sigue en «nueva» tras 5 días.** Es la única solicitud registrada en el Centro. No consta que se haya contactado.
- **La bio ya está actualizada** (leída hoy en Buzzfy): «Apps y webs a medida para tu negocio · El Jambo que sabe y las IAs, cada día · Prueba gratis, sin tarjeta ni compromiso», con enlace a `/solicitar?src=instagram`. El nombre visible no lo devuelve la API (n/d); el embudo anterior lo daba como «IA Fácil», cambio pendiente hasta ~25/11.
- **Palabras clave y DMs:** 0 comentarios y 0 respuestas en 7 días; los DMs siguen sin poder leerse (n/d, falta el permiso de mensajes).
- **Regla de promoción de 10 €:** no consta que ninguna pieza la cumpla (la mayor pieza medida el 12/11 llegó a 255 de alcance; hacen falta ≥ 500, compartidos o guardados y retención). No se propone gasto.

## 1. Cifras de hoy (Buzzfy 6-13/11; Instagram puede retrasarse 48 h)
| Etapa | 6-13/11 (7 d) | Lectura |
|---|---|---|
| Alcance total / no seguidores | 929 / 872 (59 seguidores) | Reels 895, carruseles 48, historias 46 |
| Visualizaciones | 1.900 (reels 1.179; carruseles 455; historias 266) | Solo orgánicas |
| Visitas al perfil | 15 (1,7 % del alcance a no seguidores) | **Paso más débil** |
| Toques al enlace / clics al sitio web | 0 / 4 (27 % de las visitas) | El enlace nuevo lleva a `/solicitar?src=instagram` |
| Solicitudes en el Centro | 0 nuevas (1 en total, del 8/11, «nueva») | `SolicitudInfo` no tiene nada desde el 8/11 |
| Clics registrados en el Centro (`Clic`) | 1 desde la bio (12/11, aj-reparacion-web) | `/solicitar` no crea `Clic`: solo lo hacen `/ir/<app>` |
| Interacciones | 107 (54 me gusta, 22 reposts, 13 compartidos, 5 guardados, 0 comentarios) | Los compartidos son la señal más útil |
| Cuentas que interactúan | 14 | |
| Seguidores | 1.601; 6-10/11: +0 / -2 = -2 | 11 y 12/11 pendientes de Instagram |
| DMs con intención | n/d | Falta el permiso de mensajes en Buzzfy |

## 2. Por pieza y producto
- **Episodios de «El Jambo que sabe y las IAs»:** el 301 llegó a 255 cuentas en 21 h, con 30,6 % de abandono, 10,6 s de visualización media y 0 compartidos (lectura del 12/11). Los episodios siguen siendo el motor de alcance; no consta que ninguno haya llevado visitas al perfil atribuibles.
- **Gestión Integral 7D:** 0 clics organizados en el Centro desde el 1/11 (solo una prueba interna). La única señal es el carrusel «ruta de visitas» para comerciales (27 de alcance y 1 compartido, 8/11): muestra mínima.
- **Apps a medida:** 1 solicitud (8/11, origen «demo», sector «Academia / formación»). Puede ser una prueba interna; sin contactar.
- **AJ Web / web a medida:** el único clic de bio registrado (12/11) apunta aquí. Muestra de una sola visita: se vigila, sin conclusión.

## 3. Diagnóstico
1. **Alcance → visita al perfil sigue siendo el cuello de botella.** 15 visitas por cada 872 cuentas no seguidoras. El alcance no falta; falta una razón para entrar al perfil.
2. **Visita → clic es razonable** (27 %). La bio ya promete prueba gratuita y lleva al formulario; el problema está antes.
3. **Clic → solicitud no se puede medir bien.** Instagram cuenta 4 clics al sitio, pero el Centro solo registra clics en `/ir/<app>`. Entrar a `/solicitar` no deja rastro hasta que se envía el formulario. Con 0 solicitudes nuevas, no hay conversión que medir todavía.
4. **El experimento de la fórmula v9 sigue confundido por la hora** (pivote a las 13:40 frente a control a las 18:40 y 20:40). La directiva fija la lectura del 18/11 y la del 23/11; no se cambia.
5. **Los textos antiguos siguen en el perfil** (publicaciones repetidas con «escríbeme IDEA» en la lectura del 12/11). Contradicen el cierre único y la bio nueva.

## 4. Acciones para el Estratega (por orden de efecto)
1. **Un motivo para visitar el perfil en cada pieza sin producto, desde el 13/11.** Última línea del texto y comentario fijado con «Episodio nuevo cada día en @neogestlab», y `avance_siguiente` que nombre el episodio de mañana. Cada pieza lleva en `post.json` el bloque `monetizacion` con `objetivo: visita_perfil`. Medida: visitas al perfil por cada 100 cuentas no seguidoras alcanzadas al día (hoy 1,7; meta ≥ 3).
2. **Mejora: registrar la llegada al formulario antes del 15/11 a las 13:40.** En `src/pages/Solicitar.jsx`: (a) un `Clic` al cargar la página, con `origen` = `src`; (b) un desplegable opcional «¿Qué te interesa?» (Gestión Integral 7D, app a medida, web, otra), relleno si llega `app`, guardado en `producto_slug`. Sin esto, la solicitud de quien entra por la bio llega sin producto y no dice qué interesa. No se añade `&ref=` a los textos (no es clicable en Instagram). Sin este cambio no se puede medir la conversión.
3. **Verificar la cola antes de la lectura del 18/11.** Según la lectura del 12/11 había dos choques de hora (403 el 13/11 a las 13:40; 405 y 505 el 19/11 a las 13:40). Sacar el choque antes de que el experimento de pivote compare horas. No re-verificado hoy: lo confirma el Estratega en `cola/`.
4. **Medir los compartidos por pieza (13 en 7 días).** Pedir a Calidad que mire qué piezas los generan y que las repita con el mismo gancho. Es la señal de distribución más barata que tiene la cuenta.
5. **Pieza de producto con prueba de igualdad (desde el 16/11).** Un vídeo del Centro aprobado por Calidad sale con `prueba_no_seguidores`, a las 13:40 y nunca en el hueco de un episodio; a las 48 h se compara con los episodios con la misma distribución. Si no llega a 50 cuentas no seguidoras (meta por reel), el producto viaja solo dentro de los episodios.

## 5. Vías de ingresos (sin cambios)
- Única vía realista hoy: clientes de apps a medida, Gestión Integral 7D y pruebas gratuitas. Las herramientas de monetización de Instagram y los afiliados dependen de umbrales que no se cumplen (fuentes en `monetizacion_v4_archivo.md`; no se han vuelto a verificar hoy).
- Promoción de 10 € (regla del dueño, 8/11): alcance ≥ 3× la mediana y ≥ 500 cuentas, más compartidos ≥ 1 % o guardados ≥ 2 %, más retención, a las 48-72 h. Nada se activa sin el visto bueno del dueño.
- Ingresos confirmados: 0 €. `leads.json` no cambia hoy: no hay solicitudes nuevas.

## 6. Pendiente del dueño (solo él puede)
1. Revisar la solicitud del 8/11 en `/panel/solicitudes`: marcarla como contactada o decir si fue una prueba (5 días en «nueva»).
2. Reconectar Buzzfy con el permiso de mensajes (buzzfy.co/connect/instagram?feature=messaging); sin él no se cuentan los DMs.
3. Archivar las publicaciones repetidas y quitar «escríbeme IDEA» de los textos antiguos (la API no archiva). La lista está en la versión 7.1 de este archivo (git).
4. Nombre visible → «Neogest Lab · Apps a medida» (Instagram lo bloquea hasta ~25/11).
5. Decir si alguna app tiene plan de pago. Sin precio no hay ingreso medible.

Próxima revisión: viernes 13/11 por la noche (48 h del 301 y de los episodios 302 y 303; primer dato del clic de bio del 12/11 con su ruta).

## 7. Pasada extraordinaria 13/11 12:26 UTC (orden del dueño 13/11 13:23: «arranca todo y mejora en todo»)
Cifras leídas de nuevo (Buzzfy 6-13/11 y Centro): 872 cuentas no seguidoras alcanzadas, 15 visitas al perfil, 4 clics a la web, 1 solicitud en total (la del 8/11, sin contactar), 0 nuevas, 1 clic desde la bio registrado (12/11 19:55, aj-reparacion-web). `equipo/leads.json` y `equipo/kpi_buzzfy.json` quedan actualizados con estas cifras.

**Punto exacto donde se pierde la gente: alcance a no seguidores → visita al perfil.** De 872 cuentas no seguidoras, 857 no entran al perfil (98,3 %; meta ≥ 3 %). Es el único paso que queda muy por debajo de su meta. Visita → clic sí cumple (27 %, meta ≥ 25 %). Hay un segundo agujero que no se ve: 4 clics a la web y 0 solicitudes, pero `/solicitar` no registra clics, así que no sabemos si se pierden en la página o en el formulario. Esto lo arregla el encargo a Mejora de la sección 4, acción 2.

**Tres arreglos concretos para alcance → perfil:**
1. **Rótulo fijo desde el segundo 0 en cada episodio sin producto:** «@neogestlab · episodio nuevo cada día», pequeño y en pantalla todo el tiempo. El espectador medio se va en el segundo 10,6 y el cierre llega en el 21,4, así que la invitación no puede vivir solo en el último fotograma. Responsable: Creador, en cada render nuevo (y en los que se recorten). Medida: visitas al perfil por cada 100 cuentas no seguidoras a 48 h, hoy 1,7.
2. **Que el perfil prometa lo que el reel enseñó (dueño):** archivar las publicaciones repetidas y fijar tres: «Una idea, una app», «Así se hace» y «A medida». La API no fija ni archiva, así que lo hace el dueño desde la app. Es lo primero que ve quien entra desde un reel.
3. **Medir visitas al perfil por pieza, no solo por cuenta:** el Analista cruza cada día las visitas que da cada episodio (ig_post_stats) y lo anota en kpi_buzzfy.json. Si un episodio lleva dos días sin llegar a 3 visitas por cada 100 no seguidores, el Estratega cambia su línea de perfil antes del siguiente. Así se sabe qué formato manda gente al perfil y no se espera a la lectura del 23/11.

Próxima revisión: viernes 13/11 por la noche (48 h del 301 y de los episodios 302 y 303; primer dato del clic de bio del 12/11 con su ruta).
