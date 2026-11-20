# Serie «El Jambo que sabe» (biblia v3, 16/11/2026, orden del dueño)
Sustituye a la biblia v2 (10/11/2026). Mismo nombre de serie y mismo espíritu (humor negro y satírico contra la cultura del trabajo y la burocracia, nunca contra personas reales), pero reparto nuevo y moraleja de cierre obligatoria en todos los episodios, no solo cuando «la receta del estudio la pide». Cualquier tipo de negocio. Sin apps de Neogest Lab en el vídeo. CADENCIA: la vigente en `DIRECTIVA_VIGENTE.md` §8 manda sobre cualquier cifra antigua de este documento.

## Personajes (orden del dueño 16/11; sustituyen a Jambo, Jupillo, Pelota, Bola y Trámites)
- **Rosa Melano** (humana, jefa tirana). Abusa del trabajador pidiéndole cosas absurdas, imposibles o injustas; nunca da las gracias; se lleva el mérito cuando algo sale bien y la culpa la paga siempre otro. Voz: es-ES-ElviraNeural, pitch −4 Hz. Dibujo pendiente en `src/studio/characters.js` de Neogest Studio: traje chaqueta, tacón que resuena, móvil siempre en la mano.
- **Felipe Lotas** (humano, empleado). El que recibe el marrón primero. Cara de empanado: reacciona siempre un segundo tarde, parpadeo lento, boca medio abierta. Voz: es-ES-AlvaroNeural, rate −4 %, pitch −2 Hz.
- **Sindy Entes** (humana, empleada). Le faltan todos los dientes salvo 3; sonríe igual y habla con un ligero silbido. Mucho carácter: es la que planta cara a Rosa, la lengua más larga de la oficina. Voz: es-ES-XimenaNeural, rate +8 %, pitch +4 Hz.
- **Neo** (IA, nombrada en honor a Neogest Lab). La que resuelve todo: entra siempre en el giro, nunca se altera, deja a Rosa sin argumento. Voz: es-ES-AlvaroNeural, pitch 0 (distinto de Felipe por el rate/pitch).
Catchphrase nueva (sustituye a «Que lo haga la Jupillo»): **«Que lo resuelva el Neo»** — la dice Felipe o Sindy justo antes del giro.
Formas y colores distintos por personaje; nombre en texto cuando hablan.

## Tono y límites del humor negro (sin cambios respecto a v2)
- Negro y satírico contra el sistema, la cultura del trabajo y la burocracia, no contra personas reales ni grupos. Rosa es la que se castiga con ironía en el giro; Felipe y Sindy cargan con el abuso hasta que llega Neo.
- Prohibido: suicidio, autolesión, enfermedades o muertes reales, víctimas, política de partido, colectivos, marcas ni empresas reales, consejos médicos, legales o financieros.
- Todo es ficción de personajes; la moraleja es el único tramo en serio.

## Estructura de episodio (15-25 s)
Bucle de retención de 4 pasos (orden del dueño 20/11, igual que el bucle de dopamina del casino): **apuestas** (algo que Felipe o Sindy pierden de verdad si Rosa se sale con la suya) → **pregunta** (el espectador se queda con la duda de qué va a pasar, no solo con el planteamiento) → **giro** (una sorpresa real, no lo que el espectador ya veía venir) → **reenganche** (el cierre abre el siguiente bucle antes de que el anterior se sienta resuelto del todo). Si un episodio no deja clara esa apuesta o esa pregunta, el gancho está mal escrito aunque cumpla el límite de palabras.
1. Gancho ≤ 8 palabras en pantalla desde el fotograma 0 («Cuando tu jefa te pide algo "para ayer"»). Debe dejar clara la apuesta: qué pierde Felipe o Sindy si esto sale mal. La IMAGEN sola (sin leer el texto ni oír nada) tiene que entenderse en los primeros 0,5 s: el texto confirma, no explica desde cero. El último fotograma del cierre vuelve a la misma pose/plano/elemento del gancho, para que el episodio se pueda ver en bucle sin notar el corte (orden del dueño 20/11: "vídeos completamente adictivos").
2. Planteamiento en una frase que añade la pregunta: Rosa pide algo absurdo a Felipe o Sindy, de forma que el espectador se pregunte qué va a hacer para salir de esta (no solo "qué pide Rosa", sino "y ahora qué").
3. Escalada en 3 golpes, cada uno peor que el anterior; sin silencios > 0,6 s. Cada golpe mantiene la pregunta abierta y la hace más urgente.
4. Giro: entra Neo y resuelve ESE conflicto con un desenlace que sorprenda (no el que ya se veía venir), dejando a Rosa en evidencia. «Que lo resuelva el Neo» solo si es el remate, no una muletilla.
5. **Moraleja (obligatoria, 6-9 palabras, tono serio, fotograma guardable) + reenganche: pregunta o gancho de la parte 2, de forma que el bucle no se cierre del todo.** Cuando exista una cifra real verificada que encaje, va en pantalla pequeña con su fuente.
Pie del post: línea 1 con cifra o POV; 2-4 contexto; línea 5 un único pedido (enviar o guardar); fuente de la cifra si la hay; 1-5 hashtags (#humornegro #trabajo #ia #jefes #pymes). Sin enlace ni «prueba gratuita» durante la fase sin apps.

## Datos reales para moralejas con cifra (heredados de la biblia v2, ya verificados; confirmar la fuente primaria antes de reutilizar cada cifra)
| Cifra | Dato | Fuente leída | Matiz |
|---|---|---|---|
| Horas extra no pagadas | 2,5 millones de horas a la semana en el 1T 2026; el 42 % de las horas extra no se cobra (5,89 M semanales, 3,38 M pagadas) | El Español, 26/05/2026, citando la EPA del INE | Confirmar en ine.es. Cifras en euros y empleos del mismo texto son estimaciones de UGT/CCOO sin metodología: no usarlas. |
| Administración en pymes | El 55 % de las empresas cree que las tareas administrativas le quitan tiempo para lo estratégico | Forbes España 22/04/2026, informe Qonto + IO Investigación («Radiografía económica y bancaria de la micro y pequeña empresa en España 2026») | Lo encarga una fintech: decir siempre «según un informe de Qonto». El dato de «15 % más de 10 días al mes» de la versión v2 era solo de tareas bancarias: no usarlo. |
| Plazo legal de pago | 30 días por defecto y, por pacto entre empresas, nunca más de 60 días naturales | BOE, Ley 3/2004 art. 4 (consolidado, en vigor desde 28/07/2013) | Información general, no asesoramiento legal; no pronunciarse sobre casos concretos. |
| Registro de jornada | Obligatorio para todas las empresas desde el 12/05/2019 (registro diario de la jornada de cada trabajador) | Estatuto de los Trabajadores, art. 34.9, Real Decreto-ley 8/2019 | Información general, no asesoramiento legal. |
(Retirado de v2 por falta de fuente fiable: el dato de «200 horas/año de papeleo» y «47 horas semanales» de ATA, por ser específico de autónomos y no encajar con la relación jefa-empleado de este reparto. Si se reutiliza en el futuro, solo en un episodio protagonizado por un autónomo, no por Felipe/Sindy como empleados.)

## Primeros 6 episodios (reescritos sobre las mismas situaciones y cifras ya verificadas de v2, con el reparto nuevo)
1. **«Cuando tu jefa pide un "momentito" a las 18:55.»** Rosa: «Felipe, un momentito antes de irte.» El momentito dura hasta las 23:00; Felipe y Sindy encadenan tareas que «no son nada». Giro: Neo registra las horas extra reales de ese mes. Moraleja: «Cada semana se trabajan 2,5 millones de horas extra sin cobrar (EPA, 1T 2026).»
2. **«La reunión para decidir si hace falta la reunión.»** Rosa convoca una reunión sobre si otra reunión es necesaria; Sindy pregunta si esta lo era; Felipe no entiende nada. Giro: Neo resume las tres reuniones en un correo de dos líneas que ya lo resolvía todo. Moraleja: «El 55 % de las pymes cree que la administración le resta tiempo para lo importante (informe de Qonto).»
3. **«Aquí no hay horario, hay resultados.»** Rosa redefine el horario de Sindy como «resultados» que solo se consiguen quedándose hasta las nueve. Felipe pregunta si eso no es tener horario igual. Giro: Neo mide los resultados reales de Rosa (cero horas trabajadas) y sube el sueldo de Felipe y Sindy con lo que ahorra. Moraleja: «"Resultados, no horario" casi siempre significa las mismas horas sin pagarlas.»
4. **«Contraté una IA para no contratar a nadie... y le metí el doble de trabajo a la plantilla.»** Rosa presume de haber «modernizado» la empresa con IA mientras sigue sobrecargando a Felipe y Sindy. Giro: Neo se niega a cubrir el puesto que Rosa no quiere pagar y expone la cuenta. Moraleja: «La IA no se cansa. Tú sí. Eso no es un fallo tuyo.»
5. **«El cliente que paga a 90 días (y Rosa le da precio de amigo).»** Un cliente pide descuento «de amigo»; Rosa se lo concede a costa del sueldo de Felipe. Giro: Neo corrige el presupuesto al plazo legal. Moraleja: «El plazo máximo legal de pago entre empresas es de 60 días naturales (Ley 3/2004).»
6. **«Aquí somos una familia (pero solo hereda el cuñado).»** Rosa pide un sábado gratis «porque somos una familia»; Sindy responde que en su familia los sábados se cobran. Giro: Neo da de alta las horas extra de los últimos sábados. Moraleja: «Registro de jornada obligatorio desde 2019 (art. 34.9 del Estatuto de los Trabajadores).»
(Sin cifra todavía — usar solo moraleja sin estadística hasta encontrar fuente fiable, como el episodio 4 de arriba): ideas de reserva — «la subida de sueldo "simbólica" del 0 %», «el café cronometrado», «la oferta de "becario con 10 años de experiencia"».

## Producción
- Dibujo pendiente (Mejora, en `src/studio/characters.js` de Neogest Studio): Rosa, Felipe, Sindy y Neo con formas simples, un acento de color cada uno, sin rasgos que los hagan reconocibles como personas reales o colectivos concretos. Los dientes de Sindy son un gag de personaje, no una burla a nadie real.
- Creador: ver `herramientas/estudio/gen_episodios.py` (slugs `rosa`, `felipe`, `sindy`, `neo`, `cliente`) y `herramientas/estudio/LEEME.md`.
- Calidad: añade a su checklist v9 que la moraleja esté siempre presente y que ninguna cifra se publique sin la fuente de la tabla de arriba (o una nueva, verificada antes de usarla).

## Registro de cambios
- 2026-11-16 · orden del dueño · biblia v3: reparto nuevo (Rosa Melano, Felipe Lotas, Sindy Entes, Neo), moraleja de cierre obligatoria en todo episodio, episodios 1-6 reescritos sobre las mismas cifras verificadas de v2. Retirado el dato de ATA (autónomos) por no encajar con la relación jefa-empleado del reparto nuevo.
