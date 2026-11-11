# Monetización de @neogestlab (Neogest Lab · escaparate de apps)

Analista de monetización. Versión 6: 11/11/2026 ~22:00 CET (revisión diaria, orden del dueño «monetizar, obsesivo»). Sustituye a la v5 del 8/11 (en git). Rige DIRECTIVA_VIGENTE.md (no se toca). Vías de Instagram y afiliados con fuentes: `monetizacion_v4_archivo.md`.
Regla: lo que no he leído en una fuente se marca «no consta». Sin gasto ni promociones sin visto bueno del dueño.

## 0. Resumen ejecutivo
- **Embudo 28/10-11/11 (Buzzfy, 14 días):** 568 cuentas no seguidoras alcanzadas → 14 visitas al perfil (2,5 %) → 3 clics al sitio web (21 %) → **1 solicitud registrada en el Centro (dudosa, ver §2)** → 0 € de ingresos. Seguidores 1.602; del 28/10 al 8/11: 4 altas y 12 bajas (-8 netos).
- **Hallazgo nuevo y más importante: el alcance y la venta están en piezas distintas.** El episodio de El Jambo (humor negro) de hoy tiene **120 cuentas de alcance en 2,9 h**, 34 % de saltos y 10 s de visualización media. Los 6 reels de app/web de los últimos 3 días alcanzan **3-14 cuentas** (mediana 6) con 50-88 % de saltos. Es ~20 veces más alcance, pero el episodio no lleva oferta ni enlace (la directiva lo manda así) y las piezas con oferta no las ve nadie.
- Lectura honesta: el cuello de botella ya no es solo «gancho → visita». Es que **no hay ningún puente entre la audiencia que sí llega (episodios) y la oferta (prueba gratuita)**. La fórmula v9 (episodio + pivote de UNA función de app + cierre único) es exactamente ese puente; el bloque 501-508 empieza el 15/11.
- El enlace de la bio ya apunta a `/solicitar?src=instagram` (cambiado 11/11 21:12 CET). Aún no hay datos posteriores: primera lectura útil el 13/11.

## 1. Cifras (Buzzfy, datos hasta 11/11 20:40 UTC; retraso de hasta 48 h)
| Etapa | Dato | Lectura |
|---|---|---|
| Alcance 14 d | 619 cuentas (568 no seguidoras, 51 seguidoras); reels 581, carruseles 46, historias 38 | Casi todo llega a desconocidos; los reels son el único formato que alcanza |
| Visualizaciones | 1.421 (reels 810, carruseles 419, historias 192) | |
| Interacciones | 104: 52 me gusta, 5 guardados, 13 compartidos, 21 reposts, 0 comentarios | Los compartidos existen; nadie comenta |
| Visitas al perfil | 14 (2,5 % de los no seguidores; meta ≥ 3 %) | Paso más débil según `embudo.md` |
| Clics al sitio / toques al enlace | 3 / 0 (21 % de las visitas; meta ≥ 25 %) | Medición previa al cambio de enlace |
| Solicitudes en el Centro (`SolicitudInfo`) | 1 total (8/11 21:40), estado «nueva» | Ver §2 |
| Clics registrados en el Centro (`Clic`, por producto) | 32 desde el 30/10; solo 3 con `l.instagram.com` (todos el 8/11); ninguno desde Instagram el 9-11/11 | La web casi no recibe tráfico de Instagram |
| DMs con intención / automatizaciones | **no medible**: `ig_inbox` falla (permiso de mensajes sin aprobar en Buzzfy) y las automatizaciones son plan MAX | Enlace de reconexión: buzzfy.co/connect/instagram?feature=messaging (solo el dueño) |

## 2. Lo que sí he podido leer del Centro (Base44, solo lectura)
- Esta sesión puede leer las entidades `SolicitudInfo` y `Clic` del Centro con las herramientas de Base44 (antes se anotaba «no accesible»). Lo he dejado en `leads.json` solo como contadores, sin nombres ni emails.
- **Única solicitud:** 8/11 21:40, `origen: demo`, producto `app-a-medida`, sector «Academia / formación», estado **nueva** (nadie la ha marcado como contactada en 3 días). Cae 7 min después de un clic con referer del panel del propio Centro, así que **puede ser una prueba del equipo**; no puedo confirmarlo. Si es real, es el primer cliente potencial y está sin atender.
- Los clics `origen: bio/ig` por producto se repartieron entre gps-andaluz, aj-sistema-taller, medicator, insultator y expedientes-imposibles: el tráfico llegó a apps que hoy no se promocionan o a un hub retirado. Ninguno a Gestión Integral 7D desde Instagram.
- `SolicitudInfo.origen` solo recoge `demo`; `src=instagram` y la pieza de origen no quedan atribuidos por defecto. Sin eso no se sabe qué reel vende.

## 3. Por qué (datos reales, no suposiciones)
- Episodio Jambo (11/11 17:43 UTC, 2,9 h): alcance 120, 149 visualizaciones, 2 me gusta, 0 compartidos, saltos 34,4 %, media 10 s. Provisional, pero ya supera a cualquier pieza de app.
- Reels de app/web (8-10/11): alcance 3-14, saltos 50-88 %, media 5-26 s. El mejor por compartidos es Studio Beats PRO (1 compartido sobre 14 de alcance) y MEDICATOR (1 sobre 8): ruido, muestra mínima.
- Carruseles: 3-10 de alcance (0,19-0,65× la mediana de feed de 15,5). No captan.
- Conclusión: con 1.600 seguidores y un algoritmo que reparte el contenido de entretenimiento a desconocidos, la venta tiene que viajar **dentro** del contenido que sí se distribuye, no en piezas de producto puras.

## 4. Recomendaciones para el Estratega (3-5 acciones, por orden de efecto)
1. **Dar prioridad a los episodios con pivote (501-508, desde el 15/11) y no retrasarlos por nada.** Cada uno cierra con UNA función verificada, el cierre único («Pide tu prueba gratuita…») y el enlace a `/solicitar?app=<slug>&src=instagram` en el texto. Experimento de la semana 16-22/11 (el 1 de cada 3 sin producto de la fórmula v9 ya es el grupo de control): comparar a 48 h visitas al perfil por cada 100 de alcance en episodios con pivote frente a sin pivote. Si el pivote no sube las visitas ≥ 3/100, cambiar el pivote por la oferta en el último fotograma, no por más producto.
2. **Atribuir cada pieza.** Pedir a Mejora que el enlace de cada texto lleve `&ref=<id de pieza>` y que `/solicitar` guarde `src` y `ref` en `SolicitudInfo.origen` (hoy solo guarda «demo»). Sin esto no hay forma de saber qué reel trajo la primera solicitud.
3. **No subir el volumen de piezas de producto puras.** Con alcance 3-14, más reels de app solo diluyen. Mantener 1 reel de app y 1 carrusel de app por semana (§10) y darles el gancho que ya mueve a la cuenta (dolor concreto + humor negro: cobros a 60-90 días, factura con enlace de pago, de `virales_semana.md` fórmula 1). El resto de huecos, episodios o en blanco.
4. **Leer el embudo el 13/11 y el 18/11 con una regla fija.** Si tras el cambio de enlace visita → clic sigue < 25 % o clic → solicitud es 0 en 7 días, el siguiente experimento (semana del 23/11) es la oferta del título del enlace: «Prueba gratuita» frente a «Cuéntanos tu idea: te decimos cómo sería tu app» (la segunda sirve a quien no sabe qué app quiere). Solo el dueño cambia el título del enlace.
5. **Atender lo que ya existe.** Pedir al dueño que (a) marque la solicitud del 8/11 como contactada o descartada en `/panel/solicitudes` (o confirme que fue una prueba) y (b) reconecte Buzzfy con permiso de mensajes para poder contar los DMs. Hasta entonces el indicador de DMs seguirá en «n/d».

## 5. Vías de ingresos (resumen)
- Única vía realista hoy: **captar clientes de apps a medida / Gestión Integral 7D / prueba gratuita de las apps**. Las herramientas de monetización de Instagram y los afiliados dependen de umbrales y alcance que no se cumplen (detalle y fuentes en `monetizacion_v4_archivo.md`; no se han vuelto a verificar hoy).
- **Promoción de 10 €** (regla del dueño 8/11): solo con pieza que ya funcione orgánicamente a 48-72 h: alcance ≥ 3× la mediana y ≥ 500 cuentas, + compartidos ≥ 1 % o guardados ≥ 2 %, + retención. Hoy ningún reel llega a 500 (el episodio de hoy: 120 en 2,9 h; revisar a las 48 h el 13/11). Si cumple, aviso al dueño; no se activa nada sin su visto bueno. La cuenta publicitaria sigue sin método de pago ni Instagram vinculado (v5).
- Nada de ingresos confirmados: `leads.json` mantiene 0 € hasta que el dueño lo confirme.

## 6. Pendiente del dueño (solo él puede)
1) Revisar la solicitud del 8/11 en `/panel/solicitudes`. 2) Reconectar Buzzfy con permiso de mensajes. 3) Nombre visible → «Neogest Lab · Apps a medida» (Instagram lo bloquea hasta ~25/11). 4) Quitar o editar a mano los textos antiguos que aún dicen «escríbeme IDEA» (reels 8-9/11 y carruseles): contradicen el cierre único. 5) Decir si alguna app tiene plan de pago (sin precio no hay ingreso medible).
Próxima revisión: jueves 12/11 (embudo diario) y lectura a 48 h de los episodios el 13/11.
