# Monetización de @neogestlab (Neogest Lab · escaparate de apps y webs)

Analista (incluye monetización). Versión 10: 21/11/2026 01:30 UTC (pasada semanal de embudo). Sustituye a la v9 del 15/11. Rige equipo/DIRECTIVA_VIGENTE.md (no se toca). Vías de Instagram y afiliados con fuentes: `monetizacion_v4_archivo.md`.
Regla: lo que no se ha leído en una fuente va como «no consta» o «n/d». Sin gasto ni promociones sin visto bueno del dueño.
Fuentes de hoy, solo lectura: Buzzfy (`ig_account_stats`, `ig_follower_growth`, `ig_inbox`, `ig_comments`; ventana 14-21/11) y Base44 del Centro (`SolicitudInfo`, app 6ae5244d4e2b32702f0a3cd6). `equipo/kpi_buzzfy.json` y `equipo/leads.json` actualizados; `equipo/embudo.md` regenerado con `herramientas/embudo.py`.

## 0. Resumen ejecutivo (14-21/11, 7 días)
- **Embudo:** 3.913 cuentas no seguidoras alcanzadas → **2 visitas al perfil (0,1 %; meta ≥ 3 %)** → **1 clic al sitio (50 %)** → **0 solicitudes nuevas en el Centro** → **0 €**.
- **El paso más débil sigue siendo alcance → visita al perfil**, y ha empeorado: 0,5 % la semana anterior (8 de 1.770) y 0,1 % ahora (2 de 3.913). Con 2 visitas no se puede sacar una conclusión firme, pero la tendencia es clara: el alcance crece y no llega al perfil.
- **Lectura del 100 % del último paso:** `embudo.md` marca «1 de 1 solicitudes» (100 %). Es un artefacto: la única solicitud del Centro es del 8/11, origen demo, fuera de la ventana. No hay ninguna solicitud dentro de 14-21/11, así que este paso no se puede medir todavía.
- **Seguidores:** 1.600 ahora (−2 netos en 13-17/11 ya finalizados; 18 y 19/11 pendientes en Instagram). Sin caída brusca.
- **Alcance:** casi todo es reel (3.948 de 3.954 cuentas por tipo). Sigue sin llegar a quien ve el reel: las visitas al perfil no suben con el alcance.
- **Interés en apps a medida y en Gestión Integral 7D:** n/d en esta ventana. La única solicitud del Centro es de «App a medida» (demo, 8/11). No hay solicitudes de Gestión Integral 7D. `/solicitar` no registra por qué app se entra, así que el interés por producto no se puede separar.

## 1. Lo que dicen las piezas (muestra pequeña, confianza baja)
- **Compartidos:** 8 en la semana; **guardados:** 0; **comentarios:** 0; **«me gusta»:** 65; **reposts:** 24. Ningún comentario sin responder en los 10 posts más recientes.
- **Mensajes directos (`ig_inbox`):** en 14-21/11 solo hay 1 hilo nuevo, con un mensaje sin texto del 14/11 23:09 y la ventana de 24 h cerrada. Hay 1 hilo con la palabra «Precio» (10/11) sin respuesta registrada, también con la ventana cerrada. Es la única señal de intención de compra del periodo y no consta que nadie la haya atendido. Otros hilos son antiguos (2024-2025) o de cuentas propias del dueño.
- **Palabras clave:** no hay palabras clave activas en esta ventana (no se usa la fórmula «palabra clave → DM», prohibida por la directiva). Los mensajes «Precio» e «Idea» son de un solo perfil y se dejan como n/d de tendencia.
- **Tiempo medio visto y % de retención:** n/d en esta pasada (no se leyó `ig_post_stats`).

## 2. Embudo y Centro
- Clic → solicitud: **0 nuevas**. La única solicitud (8/11, demo) está cerrada desde el 14/11 22:08. Quién la cerró y si hubo contacto no consta. No se contacta a nadie sin que lo pida (LSSI art. 21).
- Clic de /solicitar: no se registra (pendiente de Mejora desde el 14/11).
- Pruebas gratuitas: n/d. Ingresos confirmados: 0 €.

## 3. Acciones para el Estratega (4)
1. **Que el perfil prometa lo que el reel enseña (alcance → perfil, 0,1 %).** En cada reel de la semana, el texto fijado y el cierre deben decir qué resuelve la app de la que habla el reel y llevar a la bio. Medir visitas al perfil a 48 h por pieza, no solo vistas. Meta: 3 % de no seguidores → perfil antes de decidir nada más.
2. **Cierre de prueba gratuita con `app=<slug>` en cada enlace de Gestión Integral 7D y de App a medida** (`/solicitar?app=<slug>&src=instagram`), según la directiva §8. Así, cuando haya solicitudes, se verá qué producto las genera. Coordinar el slug con el Centro.
3. **Experimento de la semana 27/11 (ya planificado):** un episodio con oferta de prueba gratuita en el último plano frente a otro igual sin ella, 3 piezas por brazo, decisión por visitas al perfil y clics, no por vistas.
4. **Mejora: registrar los clics de /solicitar por app y por src** (pendiente desde el 14/11). Sin eso el paso clic → solicitud no tiene medida y el último paso del embudo seguirá en «n/d».

**Para el dueño (no es acción de Estratega):** decidir si responde a la DM con «Precio» (10/11, sin respuesta, ventana cerrada). Con la ventana cerrada, Instagram no deja responder con mensaje libre; la respuesta sería manual y solo si el dueño lo quiere. No se contacta por cuenta propia.

**No hay promoción de pago**: el alcance a no seguidores no justifica gasto y el dueño no lo ha pedido.

## 4. Programas de monetización de las plataformas
- Sin lectura nueva de fuentes oficiales esta semana: no consta nada que aplicar. Se mantiene lo de `monetizacion_v4_archivo.md`, sin dar nada por cierto.

## 5. Fuentes y límites
- Cifras de Buzzfy: de la API, con hasta 48 h de retraso (18 y 19/11 de seguidores, pendientes).
- Leads: `equipo/leads.json`, sin nombres ni emails. Las solicitudes completas solo se miran en el Centro.
- `equipo/embudo.md` compara solicitudes acumuladas con clics de la ventana; por eso el último paso sale 100 %. Corregir el script para contar solo solicitudes de la ventana.
