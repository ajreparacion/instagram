# Encargo · Recepcionista 24h (servicio nuevo, orden del dueño 16/11/2026)

Manda `equipo/DIRECTIVA_VIGENTE.md` (§9). Ficha con hechos verificados y prohibido afirmar: entidad Producto del Centro, slug `recepcionista-24h`, y doc del proyecto `claude/apps/recepcionista-24h.md`.

## Qué es
Un asistente telefónico con inteligencia artificial que atiende las llamadas de un negocio las 24 horas, da información y reserva citas. Neogest Lab lo configura y lo mantiene. Para cualquier negocio: no se presenta para un sector.

## Qué se puede decir (solo esto)
- Atiende las 24 horas, todos los días. El negocio conserva su número (desvío de llamadas).
- Nombre, voz (hasta 14) y trato de tú o de usted a medida.
- Reserva citas durante la llamada con Google Calendar, Outlook, Cal.com o Calendly.
- Tras cada llamada llega un correo con el resumen. Puede pasar la llamada a una persona.
- Responde con la información del negocio a partir de sus documentos.
- Datos en centros de datos europeos, conforme al RGPD.
- Neogest Lab hace el alta, la configuración y los cambios.
- Precio en posts: solo «desde 150 € al mes» y «sin permanencia». El detalle (alta 290 €; 190 €/mes ilimitado; 150 €/mes hasta 100 llamadas; sin IVA) va en la ficha, no en los vídeos.

## Qué NO se puede decir
Que es una persona o que «no se nota»; «ilimitado» sin precisar el plan; el nombre, la marca o el logo del proveedor de la tecnología; clientes, reseñas o cifras de ahorro; prueba gratuita o primer mes gratis; nada de emergencias, consejo médico o legal.

## Formato
Promo de app (directiva §5): 25-45 s, ANTES/DESPUÉS, voz final ElevenLabs Johnny (presupuesto §6), música en primer plano, cierre ≤ 3 s con logo 2026.
- La llamada se RECREA con voces sintéticas (narración + voz del asistente) y lleva en pantalla «Recreación» durante toda la escena. No se usa ninguna grabación de llamadas reales ni el asistente del taller.
- En la voz: «asistente telefónico» o «recepcionista virtual», nunca las siglas; cifras en letra; nunca un nombre propio como primera palabra.
- Cierre del post: «Solicita información gratuita: sin tarjeta, sin datos bancarios y sin compromiso» + `/solicitar?app=recepcionista-24h&src=<canal>`. Es un servicio a medida: NO se usa «Pide tu prueba gratuita».

## Tres guiones de arranque (el Creador los ajusta a tiempos; el Centro pone la voz)
**R1 · «¿Cuántas llamadas pierdes mientras trabajas?»**
ANTES: móvil sonando sobre una mesa de trabajo, tres llamadas perdidas en pantalla. Voz: «Estás con un cliente. Suena el teléfono. No lo coges. Ese que llamaba ya ha llamado a otro.»
DESPUÉS (Recreación): «Buenas tardes, le atiende la recepcionista virtual del negocio. ¿En qué puedo ayudarle?» · «Quería saber el horario y pedir cita.» · «Abrimos de nueve a dos y de cinco a ocho. Tengo hueco mañana a las diez, ¿se lo reservo?» Voz: «Atiende, informa y reserva la cita. Tú sigues trabajando y te llega el resumen por correo.»
CIERRE: «Nosotros lo configuramos y lo mantenemos. Enlace en el perfil.»

**R2 · «Son las diez de la noche y suena el teléfono»**
ANTES: persiana bajada, reloj 22:00, llamada entrante. Voz: «Son las diez de la noche. Tu negocio está cerrado. El cliente, no.»
DESPUÉS (Recreación): el asistente responde, ofrece cita y aparece la cita entrando en un calendario de ejemplo (datos ficticios). Voz: «La cita queda en tu calendario mientras duermes. Por la mañana tienes el resumen de cada llamada.»
CIERRE: «Abierto las veinticuatro horas sin contratar a nadie. Enlace en el perfil.»

**R3 · «No tienes que cambiar de número»**
ANTES: lista de excusas en pantalla («cambiar de número», «aprender un programa», «configurarlo yo»), tachándose una a una. Voz: «¿Un asistente que coja el teléfono por ti? Suena a lío. No lo es.»
DESPUÉS: tres pasos en pantalla: «Tu mismo número» · «Tu voz y tu trato, de tú o de usted» · «Nosotros lo dejamos funcionando». Voz: «Conservas tu número. Eliges la voz y cómo quieres que hable. Y si hace falta, pasa la llamada a una persona.»
CIERRE: «Solicita información gratuita. Enlace en el perfil.»

## Reparto
Creador: guion.json y post.json de R1-R3 (piezas 8xx) con `app_slug: "recepcionista-24h"`. Centro: voz final y render. Calidad: comprobar «Recreación» en pantalla y que no aparece el proveedor. Estratega: 1 pieza de este servicio cada 3 días hasta tener datos.
