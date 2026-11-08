# Monetización de @neogestlab (Neogest Lab · escaparate de apps)

Analista de monetización. Versión 5: 8/11/2026 19:20 CET (domingo). Sustituye a la v4 (plan por fases de afiliados/misterios), archivada en `monetizacion_v4_archivo.md` (tabla de vías de Instagram y afiliados de Amazon, aún útil como referencia). Rige DIRECTIVA_VIGENTE.md (no se toca).
Regla: lo que no he leído en una fuente se marca "no consta". Sin gasto ni promociones sin visto bueno del dueño.

## 0. Resumen ejecutivo
- El embudo de la directiva (palabra clave → DM → clic al enlace → interés en apps a medida / Gestión Integral 7D) está **a cero en lo medible y ciego en lo demás**: 0 clics al enlace, 0 comentarios, 4 visitas al perfil en 7 días, y los DMs no se pueden leer (permiso de mensajes sin verificar en Buzzfy, sin webhooks, automatizaciones solo en plan MAX).
- Cuello de botella: **del alcance a la visita al perfil**. 445 cuentas no seguidoras alcanzadas → 4 visitas al perfil (0,9 %) → 0 clics. Antes del enlace falla el gancho de cierre, no la página.
- Hallazgo de riesgo: los carruseles de hoy salieron **duplicados** (101 ×3 y 105 ×3 en 15:06-15:31 CET) y aun así alcanzan 3-12 cuentas cada uno. Los reels, en cambio, daban ~115 de alcance por pieza.
- Ingresos: 0 €. No hay plan de pago de ninguna app documentado (pendiente del dueño).

## 1. Embudo medido (Buzzfy, 1-8/11/2026 17:18 UTC; los datos tardan hasta 48 h)
| Etapa | Dato | Lectura |
|---|---|---|
| Alcance | 468 cuentas (445 no seguidoras = 95 %); reels 459, carruseles 15, historias 6, posts 2 | Se distribuye a desconocidos, que es lo que se busca |
| Reproducciones | 715 (550 de no seguidores) | Los 6 carruseles de hoy suman solo 97 |
| Señales de interés | 44 interacciones: 25 me gusta, 5 guardados, 4 compartidos, 6 reposts, 0 comentarios | Guardados y compartidos existen pero son poquitos |
| Visitas al perfil | 4 | Etapa más débil del embudo |
| Clics al enlace (`/demo`) | 0 (linkTaps 0, websiteClicks 0) | Sin tráfico a la demo |
| Palabra clave en comentarios | 0 comentarios en los 7 posts actuales | Nadie escribe APP/IDEA en público |
| DMs con intención (IDEA, APP, «¿cuánto cuesta?») | **no medible** | `ig_inbox` falla por permiso; respondidos.json vacío |
| Solicitudes en /solicitar (apps a medida, 7D) | **no medible desde aquí** | Base44 devuelve 403 al proxy; lo ve el dueño en /panel/solicitudes |
| Seguidores | 1.603; netos -2 (1-5/11; 6 y 7/11 pendientes) | Sin cambio de tendencia |

Estado del perfil leído hoy: bio y enlace ya son los de Neogest Lab (enlace `…/demo`), pero el **nombre visible sigue siendo «IA Fácil · Trucos que no sabes»** y no «Neogest Lab · Apps a medida». 7 publicaciones en la cuadrícula; los reels 001 y 013-016 ya no existen en el perfil (el dueño borró reels por la música), así que las cifras de reels son de piezas retiradas.

## 2. Por público y por producto: todavía no hay muestra
- Solo han salido dos temas con la nueva línea: **autónomos/reformas (105, Gestión Integral 7D)** y **trucos de IA genéricos (101)**, cada uno ×3 en el mismo día, todos con menos de 3,2 h. Alcance 3-12, 1 compartido en cada tema, 0 guardados, 1 visita al perfil. Es PROVISIONAL (hasta 48 h) y demasiado pequeño para elegir sector.
- Interés en **apps a medida**: no consta ningún DM «IDEA» ni solicitud. Interés en **Gestión Integral 7D**: 1 compartido en 105 (cuenta a revisar a las 48 h), nada más.
- No se ha probado todavía hostelería, hogar, mayores (MEDICATOR), música ni ocio (directiva §3). Sin esos datos no se puede decir qué sector da más DMs.
- Comparación de formato (dato real de la semana): reels 459 de alcance en total frente a 15 de carruseles. Los carruseles publicados hoy no sustituyen a los reels para captar.

## 3. Qué no se puede medir y qué hace falta
| Hueco | Causa | Arreglo |
|---|---|---|
| DMs y palabras clave | Permiso de mensajes de Buzzfy sin verificar (enlace de reconexión: buzzfy.co/connect/instagram?feature=messaging); webhooks sin suscribir; la prueba de Buzzfy vence el 8/11 18:04 UTC y automatizaciones/respuestas son MAX | Opción A: el dueño reconecta con «mensajes» marcado. Opción B (gratis): contar hilos con APP/IDEA en `respuestas_chat.py` (PAGE_TOKEN ya lee mensajes) y guardarlos en `equipo/kpi_embudo.json` |
| Origen de cada solicitud | `/solicitar` no distingue de qué reel o sector viene | Campo «sector»/«ref» en el formulario y enlace de bio `…/demo?sector=X&ref=ig` (lo monta Mejora con código, no con el builder) |
| Clics por sector | Un solo enlace en el perfil | Cambiar el enlace según el reel que se fije/impulse, o medir por `/demo?sector=` en Base44 |
| Ingresos | Ninguna app con plan de pago conocido | Pregunta al dueño (pendiente_usuario.md 3b) |

## 4. Recomendaciones para el Estratega (acciones concretas, en orden)
1. **Parar los duplicados antes de publicar más.** Pedir a Mejora que `publicar_gh.py` compruebe en Instagram (o en el registro) si la pieza ya salió antes de reintentar tras un fallo 2/3, y que el dueño borre 4 de los 6 carruseles repetidos (dejar 1 de 101 y 1 de 105). Tres copias del mismo post en 25 min dañan la imagen de la cuenta y reparten el alcance.
2. **Reels para captar, carruseles para dar confianza.** Con los datos de la semana (459 vs 15 de alcance), poner en `plan.json` los reels «Una idea, una app» en los huecos de 13:40 y 20:40 y dejar los carruseles como máximo 1 al día, a otra hora, sin repetir tema.
3. **Un solo CTA por pieza y por público, y medible:** reel de negocio → «Comenta APP» (se cuenta en comentarios, que sí leemos); reel de apps a medida → «Escríbeme IDEA por privado»; hogar/mayores → «enlace en el perfil». Registrar en plan.json qué palabra lleva cada pieza para poder cruzarla con los DMs.
4. **Probar un sector por reel en 7 días y decidir con regla fija:** hostelería, hogar, mayores, autónomos (7D), música y «a medida», sin repetir seguidos (§3). Decisión a las 48 h con lo que exista: guardados + compartidos + visitas al perfil por cada 100 de alcance, y DMs/comentarios cuando el contador funcione. El que supere a los demás en dos mediciones pasa a ser el 60 % de «Una idea, una app».
5. **Arreglar el paso reel → perfil:** que el último segundo y la última diapositiva digan en grande «Enlace en el perfil · Neogest Lab» y que el nombre visible del perfil pase a «Neogest Lab · Apps a medida» (hoy no cuadra con el contenido: pendiente_usuario.md 3c). Medir visitas al perfil por pieza (`ig_post_stats`, carruseles e historias lo dan; reels no) y objetivo mínimo: 3 visitas por cada 100 de alcance (hoy 0,9).

## 5. Vías de ingresos (resumen; el detalle con fuentes está en monetizacion_v4_archivo.md)
- Hoy la única vía realista es **captar clientes para las apps de Neogest Lab** (apps a medida, Gestión Integral 7D y las demás): no depende de umbrales de Instagram, solo del embudo de arriba.
- Herramientas de Instagram (regalos, suscripciones, marcas): umbrales sin confirmar y alcance insuficiente; no priorizar. Afiliados de Amazon: encajaban con misterios, no con esta línea; no se activan.
- **Promoción de 10 €** (regla del dueño, 8/11/2026): solo se promociona una pieza que ya funciona orgánicamente a las 48-72 h (alcance ≥ 3 × la mediana y ≥ 500 cuentas, + compartidos ≥ 1 % o guardados ≥ 2 %, + retención). Hoy ninguna pieza lo cumple y la cuenta publicitaria 966846446095574 no tiene método de pago ni Instagram vinculado. No se gasta nada. Si algo cumple en la próxima revisión, aviso al dueño por notificación.

## 6. Pendiente del dueño (lo que solo él puede ver o hacer)
1) Contar cuántos DMs con IDEA/APP/precio ha recibido desde el 7/11 y cuántas solicitudes hay en /panel/solicitudes (yo no los puedo leer). 2) Reconectar Buzzfy con permiso de mensajes o decidir si seguir con su plan (prueba vencida el 8/11). 3) Borrar los carruseles duplicados. 4) Cambiar el nombre visible del perfil. 5) Decir si alguna app tiene plan de pago.
Próxima revisión: domingo 15/11/2026, con las piezas de esta semana ya a 48 h.
