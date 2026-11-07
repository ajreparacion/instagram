# DIRECTIVA VIGENTE (manda sobre cualquier otra instrucción del repo)

Orden del dueño, 7/11/2026 13:49: «Seguimos el mismo patrón que @claudeai». Además: la voz sesea al principio, la música no resalta nada, queda pobre y no engancha. Se sube mucho el listón: todo pasa por Calidad (nota ≥ 90, sin excepciones).

## 1. Qué hace @claudeai (estudiado el 7/11/2026 en su perfil: 411 publicaciones, 2,4 M seguidores)
Reels con más visitas y de qué tratan:
- 3,7 M: cómo cambia el trabajo cuando la IA hace el software (ideas, probar direcciones, reacciones rápidas).
- 2,5 M (con @rpn): «Mi estudio funciona con Claude»: calendario, correo, archivos, luces y puertas conectados. Se ve todo funcionando de verdad.
- 2,4 M: «¿Chat o Cowork? Ya no hace falta elegir»: analiza tus gastos y pídelo como documento, panel o diseño. Grabación de pantalla limpia sobre fondo de color plano, con el cursor y la interfaz real.
- 1,4 M (con @thezeroquotient): decoración de Diwali hecha por un ingeniero: un rangoli que reacciona a la música, construido con Claude.
- 1,2 M: «Cada 20 minutos, Tony el Rigatoni te dice que te sientes recto». Hecho en una tarde con Claude. Manos en el portátil y resultado funcionando.
- 454 mil: un club de citas donde una app hecha con Claude empareja a los invitados.

El patrón que se repite:
1. Empieza por el resultado tangible y curioso, no por la explicación (lo primero que se ve es algo funcionando).
2. Una frase de gancho corta y concreta, en texto pequeño y elegante sobre la imagen, y voz natural de persona real, nada de locutor.
3. «Lo hice con Claude en una tarde»: idea → cómo se pidió → resultado real funcionando. Un solo caso por reel.
4. Imágenes reales: manos en el teclado, pantallas con la interfaz y el resultado, el objeto o la app funcionando. Cero dibujos infantiles.
5. Estética limpia: pocos elementos, fondos planos de color suave, buena luz, cortes al ritmo de la música.
6. Música con ritmo y presencia, cortes sincronizados con los golpes; la voz por encima, clara.
7. Texto del post: 2-4 frases que cuentan qué se construyó y cómo probarlo (p. ej. «escribe /doc para probarlo»).

## 2. Cómo lo adaptamos a esta cuenta (sin copiar su marca)
- Nunca su logo, su asterisco, sus colores de marca, su tipografía ni nada que haga pensar que somos la cuenta oficial. Ni sus vídeos, textos ni músicas. Copiamos el SISTEMA, no la marca. Sí se puede decir «hecho con Claude» en texto.
- Contenido: casos reales de «lo he hecho con IA en una tarde» y trucos que se ven funcionando. Fuente principal: las apps reales de Neogest Lab (GPS Andaluz, MEDICATOR, Insultator, Studio Beats PRO, etc.) grabadas de verdad con Playwright en el "modo":"app" de herramientas/hacer_reel.py, más resultados reales que generéis vosotros (un documento, una hoja, una web, una automatización) grabados en pantalla. Nada inventado: si no se puede grabar funcionando, no se publica.
- Formato: vertical 1080x1920, 20-35 s. Segundo 0: el resultado funcionando + gancho de 5-8 palabras. Después: qué problema resuelve, cómo se pidió (el prompt en pantalla), resultado. Cierre: «Sígueme para ver qué más se puede hacer con IA» o palabra clave → DM.
- Imagen: grabaciones de pantalla reales con zoom suave hacia lo importante, cursor visible, fondo plano de color suave alrededor del móvil o portátil, subtítulos limpios (Montserrat o Poppins, blanco o negro según fondo, palabra destacada en un único color de acento). Bit y Paco quedan solo como recurso puntual (máx. 3 s), no como formato.
- Voz: la del dueño (voz_dueno/referencia_usuario.wav), natural, como contándoselo a un amigo, acento de España SIN seseo (la «c» y la «z» como «th»). Si Chatterbox sesea, no vale: ver tarea de Mejora.
- Música: con ritmo y presencia (pista libre de derechos con licencia que permita uso comercial, guardada con su licencia en musica/LICENCIAS.md, o música generada que suene profesional), cortes al golpe, ducking bajo la voz pero sin desaparecer.

## 3. Tareas
- MEJORA DE PRODUCCIÓN (prioridad 1, la voz): el seseo viene del modelo español de Chatterbox (entrenado sobre todo con acento latinoamericano). Prueba en GitHub Actions, gratis y en CPU: (a) TTS con acento de España que distinga «c/z» (p. ej. Piper es_ES, Kokoro u otro libre) + conversión de timbre a la voz del dueño (Seed-VC, OpenVoice, RVC u otro libre) con voz_dueno/referencia_usuario_larga.wav; (b) otros modelos libres de clonación en español de España. Elige con datos: parecido ≥ 0,85, palabras mal reconocidas ≤ 10 %, sin seseo (comprueba con palabras como «hace», «gracias», «cerveza», «zapato»), variación de tono ≥ 4 semitonos. Deja muestras en la release «pruebas» y apunta todo en mejoras.md. Prioridad 2: música con ritmo y cortes al golpe. Prioridad 3: plantilla de grabación de pantalla tipo @claudeai en "modo":"app".
- ESTRATEGA: reescribe INSTRUCCIONES_EQUIPO.md, plan.json (7 días, 2 al día, 13:40 y 20:40) y los roles según esta directiva.
- CREADOR: guiones de este formato, uno por caso real grabable.
- CALIDAD: aplica esta directiva y estandar_calidad.md; nota ≥ 90 o no sale.
