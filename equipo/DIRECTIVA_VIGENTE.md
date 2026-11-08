# DIRECTIVA VIGENTE (manda sobre cualquier otra instrucción del repo)

> REFERENCIA DE VÍDEO DEL DUEÑO (8/11/2026 20:10): «esta es la idea para vídeos en general» → https://www.instagram.com/reel/DfXjcjiNW8k/ . Pendiente de analizar su formato (ritmo, gancho, estilo visual, audio) y copiar el sistema, no el contenido.

> MEDICATOR, PRIORIDAD (dueño, 8/11/2026 19:38): destacar sus dos funciones estrella, ya comprobadas en el código y añadidas a hechos_verificados: (1) escanear con la cámara el código de la caja del medicamento y traer los datos oficiales de CIMA, la base de datos pública de la AEMPS; (2) «Lectura de parte médico»: foto a una receta, informe o cita, la app lee el texto en el propio móvil y propone apuntar la cita o la pastilla (se revisa antes de guardar). Creador: 2 piezas esta semana (reel grabado en la app con datos ficticios + carrusel). Inventario completo ya en hechos_verificados (41 frases, 8/11). Ganchos propuestos: «Mi madre no sabe usar el móvil… y esta app le habla» (modo Muy fácil, voz, botón llamar al familiar); «Hazle una foto al papel del médico y mira lo que pasa»; «Escanea la caja y te dice si ya la tomas» (CIMA + aviso si repite componente + alerta de alergia); «Salud de la mujer» opcional (regla, síntomas, menopausia, anticonceptiva por ciclos; sin promesas médicas, previsión orientativa); «Llega a la consulta con las preguntas hechas» (hoja para el médico). NO anunciar: modo cuidador (aparcado), APK o tiendas, IA generativa, detección de interacciones, avisos push garantizados. Decir «consulta la base de datos oficial de la AEMPS», nunca «avalada/oficial de la AEMPS», nada de diagnosticar.

> SIN ORDENADOR (dueño, 8/11/2026 18:01): no hace falta ningún PC encendido; todo vive en GitHub. El workflow «Reloj» (.github/workflows/reloj.yml) lanza «Ciclo Instagram» cada 15 min dentro de Actions y se relanza solo cada ~6 h, porque el cron de GitHub se salta ejecuciones. Ningún agente debe depender del portátil ni pedir al dueño que lo encienda. El repo tiene que seguir PÚBLICO (Instagram descarga las imágenes por jsDelivr y los vídeos de la release).

> MÚSICA (orden del dueño 8/11/2026 17:59): la música tiene que RESALTAR. Borró reels porque solo se oía la voz. Máster a -14 LUFS; con voz, la música baja como mucho 6 dB mientras se habla y se oye clara entre frases; sin voz, manda la música. Calidad lo mide con ebur128 y rechaza si la música queda tapada.

Orden del dueño, 7/11/2026 23:42-23:44: **la cuenta pasa a ser el escaparate de Neogest Lab.** Sirve para vender las apps que ya existen y apps a medida para personas y negocios. Se fusiona con el proyecto de vídeos tutoriales. Formato estrella: **«Una idea, una app»**: vídeos cortos virales que captan posibles clientes. Corrección del dueño: **no centrarse solo en talleres**; hay que llegar a cualquier tipo de persona o negocio.

Sustituye el enfoque «IA Fácil · Trucos que no sabes». Se mantiene todo lo de producción de la directiva anterior: patrón de @claudeai (sistema, no marca), su voz clonada sin seseo y con énfasis, música con ritmo y cortes al golpe, y Calidad con nota ≥ 90 sin excepciones.

## 1. Objetivo y tono
- Objetivo: que quien vea un reel piense «esto me vendría bien a mí o a mi negocio» y escriba. Métricas que mandan: DMs con intención (palabra clave, «¿cuánto cuesta?», «¿me haces una?»), toques al enlace, guardados y compartidos. Los seguidores van después.
- Regla 80/20: el vídeo aporta valor y entretiene. La venta va solo en el cierre y es suave. El cliente no debe notar que solo se le quiere vender (palabras del dueño).
- Confianza: siempre la app real funcionando con datos de ejemplo. Firma «By Neogest Lab» y logo NL neón al cierre (skill neogest-marca, Montserrat).

## 2. Mezcla de contenido (por semana, 2 al día, 13:40 y 20:40)
1. **«Una idea, una app» (≈ 60 %)**: un público concreto con un problema cotidiano, y la app de Neogest Lab que lo resuelve, en pantalla real. Estructura: segundo 0 con el resultado funcionando y un gancho de 5-8 palabras dirigido a ese público («¿Llevas las citas en una libreta?»). Después 2-3 funciones reales y el cierre. 20-35 s.
2. **«Así se hace» (≈ 25 %)**: tutoriales y cómo se crea una app desde cero con IA, con el antes y el después y trozos del proceso real. Esto es lo que fusiona el proyecto de vídeos tutoriales. Da confianza: «esto lo hacemos nosotros».
3. **«¿Y si tu idea fuera una app?» (≈ 15 %)**: apps a medida. Se lanza una idea de un tipo de negocio o persona, se enseña un prototipo o demo real hecha por el equipo y se invita a contar su idea por DM. Nunca se prometen precios ni plazos en el post.
- Los reels ya en cola (017-020, trucos de IA cotidianos) se pueden publicar como contenido de valor si pasan Calidad, cambiando el cierre y el texto del post al de Neogest Lab (§5).

## 3. Públicos: rotar, NO solo talleres
Nunca dos reels seguidos para el mismo público, y como máximo 1 reel a la semana de talleres o servicios de reparación. Lista de partida (el Estratega la amplía con datos):
| Público | Ejemplos de problema | Apps reales a revisar |
|---|---|---|
| Hostelería y comercio | caja, pedidos, stock, clientes | CajaSegura IA, Gestión Integral 7D, Son Nasi Gestión |
| Hogar y familias | gastos de casa, tareas, compras | GH PLUS · Gestión Hogar |
| Mayores y quien los cuida | citas médicas, recordar la medicación | MEDICATOR |
| Autónomos y servicios técnicos | órdenes de trabajo, presupuestos, clientes | AjReparacion Gestión, AJ Sistema DEMO, Gestión Integral 7D |
| Música y creadores | hacer bases, sonidos, contenido | Studio Beats PRO, Beats Studio, Centro de Contenido Apps |
| Ocio, humor y viajes | reírse, conducir con gracia | Insultator, GPS Andaluz |
| Aficiones y tiendas pequeñas | catálogo, pedidos personalizados | PlaymoCustons |
| Cualquier negocio con una idea | «¿y si tu idea fuera una app?» | demo a medida del equipo |

**Producto estrella (orden del dueño 7/11 23:58):** AjReparacion Gestión se adapta a CUALQUIER tipo de negocio, no solo talleres. Su demo pública será AJ Sistema DEMO, que une la gestión, la web del negocio (de AJ Reparación web) con los pedidos de la web entrando en la gestión, y un centro de creación de páginas web enlazadas con la app del cliente. PUBLICADA el 8/11/2026 00:25 (https://aj-reparacion-gestion-copy-61ad5afb.base44.app). Comprobado de verdad: web pública /w/peluqueria-demo responde y un pedido desde la web entra en la gestión como pre-orden PRE-AAAA-NNNN con la etiqueta «Desde la web». Webs demo: /w/peluqueria-demo, /w/bar-demo, /w/tienda-demo. Selector «Tipo de negocio» en Ajustes y editor «Mi web» en /centro-web. Aún sin adaptar al sector: barra inferior del móvil, PDF/albaranes y la web antigua /web/*: no enseñarlos en reels de sectores que no sean servicio técnico. Cuando lo esté, se usa para muchos sectores distintos (tienda, peluquería, bar, academia, servicio técnico…).
Todas las apps llevan la marca de agua de Neogest Lab y el fondo difuminado con el logo al hacer scroll, igual que AjReparacion Gestión.

Reglas de la tabla:
- **Solo funciones reales comprobadas en la app** (skill posts-apps-neogest). Antes de guionizar una app, abrirla y anotar qué hace de verdad. Si una app no está publicada o no funciona bien, no sale.
- La regla antigua «MEDICATOR no se promociona nunca» era del canal de misterios y queda anulada. MEDICATOR sí se enseña, como organizador de citas y recordatorios: sin consejos médicos, sin prometer resultados de salud, con datos de ejemplo y el aviso «no sustituye a tu médico».
- Cero clientes, testimonios, cifras de ventas o reseñas inventados. Si no hay un caso real, se habla de «imagina que…» y se dice claramente que es una demo.
- No usar marcas ajenas como si fueran clientes.

## 4. Producción (igual que antes, resumido)
- Vertical 1080x1920. Grabación real de la app con Playwright en el "modo":"app" de herramientas/hacer_reel.py: zoom suave a lo importante, cursor visible, móvil o portátil sobre fondo plano de color suave, subtítulos Montserrat con una palabra destacada en el color de acento de Neogest.
- Voz: la del dueño (voz_dueno/), natural, con énfasis, acento de España sin seseo. Nada de clipeos ni silencios. Los posts llevan «Voz: generada a partir de la voz del autor».
- Música con licencia comercial apuntada en musica/LICENCIAS.md, cortes al golpe y ducking sin que la música desaparezca.
- Bit y Paco (los dibujos) solo como recurso puntual, de 3 s como máximo.

## 5. Texto del post y cierre
- 2-4 frases: qué problema resuelve, para quién es, cómo probarla. Cierre fijo en una de estas formas:
  - «Comenta APP y te paso el enlace» (respuesta por DM cuando la automatización esté activa; mientras no lo esté, «enlace en el perfil»).
  - «¿Tienes una idea para tu negocio? Escríbeme IDEA por privado y te digo cómo sería tu app.»
- 3-5 hashtags del público concreto (#hosteleria, #autonomos, #pymes…) más #apps y #neogestlab.

## 6. Perfil (lo deja listo el Estratega en perfil_propuesto.md y pendiente_usuario.md; la API no lo puede cambiar)
- Usuario: @neogestlab (si está cogido: @neogest.lab o @neogestlab.apps). Nombre visible: **Neogest Lab · Apps a medida** (27 caracteres).
- Bio (140/150, entregada al dueño el 7/11 23:45): «Apps para tu negocio y tu día a día 📲 / Una idea, una app: mira cómo funcionan / Tu app a medida, sin líos / Escríbeme IDEA y te digo cómo sería 👇». Título del enlace: «Ver nuestras apps». Categoría: «Desarrollador de software» o «Servicios informáticos».
- Enlace (CONFIRMADO 7/11 23:52): https://centro-de-contenido-apps-2f0a3cd6.base44.app (app «Centro de Contenido Apps», id 6ae5244d4e2b32702f0a3cd6; la raíz «/» es la página pública «Nuestras apps» y /solicitar es el formulario para pedir una app a medida, que llega al panel /panel/solicitudes). Usar /solicitar como destino del cierre «IDEA». El hub Expedientes Imposibles queda retirado del perfil. Solo con las herramientas de código del MCP de Base44, nunca el builder con prompt.
- Foto: logo NL neón. Destacadas: EMPIEZA, APPS, A MEDIDA, ASÍ SE HACE, NEGOCIOS.
- Rejilla: archivar (no borrar) lo que no encaje cuando haya 9 reels nuevos publicados. Fijar arriba 1 «Una idea, una app», 1 «Así se hace» y 1 «A medida».

## 7. Tareas
- **ESTRATEGA (ya)**: reescribir INSTRUCCIONES_EQUIPO.md, plan.json (7 días, 2 al día, con el público de cada reel y la rotación de §3) y los roles según esta directiva. Actualizar perfil_propuesto.md y el punto de perfil de pendiente_usuario.md.
- **CREADOR**: antes de guionizar, inventario de las apps reales (qué está publicado, URL y qué hace cada una de verdad) en equipo/catalogo_apps.md. Después, guiones de §2 con públicos alternos.
- **MEJORA**: página de apps y enlace (§6), plantilla «Una idea, una app» en hacer_reel.py, automatización de la palabra clave APP/IDEA en DM si las herramientas conectadas lo permiten (si no, apuntarlo en pendiente_usuario.md).
- **ANALISTA**: medir por público (qué sector da más DMs y toques al enlace) y avisar al Estratega cada semana.
- **CALIDAD**: esta directiva y estandar_calidad.md; nota ≥ 90 o no sale. Rechazo automático si aparece una función que la app no tiene, un cliente o testimonio inventado o dos reels seguidos del mismo público.

## 8. Escaparate y acceso (orden del dueño 8/11/2026 12:10)
- Las apps NO se dejan usar libremente: el público ve una demo tipo vídeo y un paseo en formato historias en https://centro-de-contenido-apps-2f0a3cd6.base44.app/demo (en construcción; se activa cuando el dueño publique) y, para usarlas, SOLICITA ACCESO en /solicitar.
- Cierre de los reels y textos de los posts: «Mira en 60 segundos lo que haría por tu negocio · enlace en el perfil» o «Comenta APP y te paso la demo». Nunca prometer acceso libre ni dar usuarios o PIN.
- Los reels se graban desde la demo con sesión del equipo; en pantalla nunca aparecen PIN, contraseñas ni emails.
- Enlace profundo por público: /demo?sector=bar, /demo?sector=peluqueria, etc. Usar el del público del reel.
