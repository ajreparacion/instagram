# Genera las 4 herramientas de demostracion (HTML de un solo archivo, sin red) a partir de base.html.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
base = open(os.path.join(HERE, "base.html"), encoding="utf-8").read()

T = {}

# ---------------------------------------------------------------- 1. presupuesto
T["presupuesto"] = dict(titulo="Presupuesto", css="""
.ln{display:grid;grid-template-columns:1fr 120px 190px;gap:14px;margin-bottom:16px}
.ln input{font-size:36px;padding:14px 18px}
.hd{display:grid;grid-template-columns:1fr 120px 190px;gap:14px;font-size:28px;color:var(--mut);margin-bottom:8px}
.tot{margin-top:24px;border-top:3px solid var(--line);padding-top:24px}
.tr{display:flex;justify-content:space-between;align-items:center;font-size:40px;margin-bottom:12px}
.tr select{width:230px;font-size:38px;padding:10px 16px}
""", body="""
<h2>Presupuesto</h2>
<div class="hd"><span>Concepto</span><span>Uds.</span><span>Precio €</span></div>
<div id="lines"></div>
<button class="sec" id="add" style="margin-top:6px;font-size:34px;padding:14px 28px">+ Línea</button>
<div class="tot">
 <div class="tr"><span>Base</span><b id="base">0,00 €</b></div>
 <div class="tr"><span>IVA</span><select id="iva"><option value="21">21 %</option><option value="10">10 %</option><option value="4">4 %</option></select><b id="ivaimp">0,00 €</b></div>
 <div class="tr" style="margin-top:22px"><span style="font-weight:600">Total</span><span class="big" id="total">0,00 €</span></div>
</div>""", js="""
const num=v=>{v=String(v||'').replace(',','.').replace(/[^0-9.]/g,'');return parseFloat(v)||0};
function addLine(c,u,p){const d=document.createElement('div');d.className='ln';d.innerHTML='<input placeholder="Concepto" value="'+(c||'')+'"><input inputmode="decimal" placeholder="1" value="'+(u||'')+'"><input inputmode="decimal" placeholder="0,00" value="'+(p||'')+'">';d.querySelectorAll('input').forEach(i=>i.addEventListener('input',calc));$('#lines').appendChild(d);calc()}
function calc(){let b=0;document.querySelectorAll('.ln').forEach(l=>{const i=l.querySelectorAll('input');b+=Math.round(num(i[1].value)*num(i[2].value)*100)});
const iva=Math.round(b*num($('#iva').value)/100);$('#base').textContent=eur(b);$('#ivaimp').textContent=eur(iva);$('#total').textContent=eur(b+iva)}
$('#iva').addEventListener('change',calc);$('#add').addEventListener('click',()=>addLine());
window.reset=()=>{$('#lines').innerHTML='';$('#iva').value='21';addLine();addLine()};
window.preset=()=>{$('#lines').innerHTML='';$('#iva').value='21';addLine('Cambiar grifo cocina','1','85');addLine('Material de fontanería','1','32');addLine('Desplazamiento','1','15')};
window.reset();
""")

# ---------------------------------------------------------------- 2. cuenta
T["cuenta"] = dict(titulo="Dividir la cuenta", css="""
.chips{display:flex;gap:16px}
.chips button{flex:1;background:#EAF0F3;color:var(--ink)}
.chips button.on{background:var(--acc);color:#fff}
.step{display:flex;align-items:center;justify-content:space-between;background:#F3F7F9;border-radius:26px;padding:12px 18px}
.step button{width:92px;height:92px;padding:0;font-size:56px;line-height:1}
.step b{font-size:64px}
.res{margin-top:34px;background:#EAF7FA;border-radius:34px;padding:36px;text-align:center}
.res small{display:block;font-size:34px;color:var(--mut);margin-top:10px}
""", body="""
<h2>Dividir la cuenta</h2>
<label>Total de la cuenta (€)</label><input id="tot" inputmode="decimal" placeholder="0,00" style="margin-bottom:28px">
<label>Personas</label><div class="step" style="margin-bottom:28px"><button class="sec" id="men">−</button><b id="pers">2</b><button id="mas">+</button></div>
<label>Propina</label><div class="chips" id="chips"><button data-p="0" class="on">0 %</button><button data-p="5">5 %</button><button data-p="10">10 %</button></div>
<div class="res"><div style="font-size:34px;color:var(--mut)">Cada uno paga</div><div class="big" id="cada">0,00 €</div><small id="conp">Total con propina: 0,00 €</small></div>""", js="""
let P=2,TIP=0;
const num=v=>{v=String(v||'').replace(',','.').replace(/[^0-9.]/g,'');return parseFloat(v)||0};
function calc(){const t=Math.round(num($('#tot').value)*100);const con=Math.round(t*(100+TIP)/100);$('#pers').textContent=P;$('#cada').textContent=eur(Math.round(con/P));$('#conp').textContent='Total con propina: '+eur(con);
document.querySelectorAll('#chips button').forEach(b=>b.classList.toggle('on',+b.dataset.p===TIP))}
$('#tot').addEventListener('input',calc);$('#mas').addEventListener('click',()=>{P=Math.min(30,P+1);calc()});$('#men').addEventListener('click',()=>{P=Math.max(1,P-1);calc()});
document.querySelectorAll('#chips button').forEach(b=>b.addEventListener('click',()=>{TIP=+b.dataset.p;calc()}));
window.reset=()=>{$('#tot').value='';P=2;TIP=0;calc()};
window.preset=()=>{$('#tot').value='86,40';P=4;TIP=5;calc()};
window.reset();
""")

# ---------------------------------------------------------------- 3. suscripciones
T["suscripciones"] = dict(titulo="Mis suscripciones", css="""
.f{display:grid;grid-template-columns:1fr 200px;gap:14px;margin-bottom:14px}
.f input{font-size:38px}
.it{display:flex;align-items:center;gap:20px;background:#F3F7F9;border-radius:24px;padding:20px 26px;margin-bottom:14px;font-size:40px;transition:opacity .3s}
.it .n{flex:1;font-weight:500}
.it.off{opacity:.38}.it.off .n,.it.off .p{text-decoration:line-through}
.ck{width:62px;height:62px;border-radius:18px;border:4px solid var(--acc);background:var(--acc);color:#fff;font-size:42px;line-height:54px;text-align:center;font-weight:700}
.off .ck{background:#fff;color:#fff}
.sum{display:flex;gap:18px;margin-top:20px}
.sum div{flex:1;background:#EAF7FA;border-radius:30px;padding:26px;text-align:center}
.sum span{display:block;font-size:30px;color:var(--mut)}
.sum b{font-size:60px;color:var(--accd)}
#ah{margin-top:18px;text-align:center;font-size:38px;font-weight:600;min-height:56px}
""", body="""
<h2>Mis suscripciones</h2>
<div class="f"><input id="nom" placeholder="Nombre"><input id="pre" inputmode="decimal" placeholder="€/mes"></div>
<button id="add" style="width:100%;margin-bottom:22px">Añadir</button>
<div id="lista" style="min-height:290px"></div>
<div class="sum"><div><span>Al mes</span><b id="mes">0,00 €</b></div><div><span>Al año</span><b id="anio">0,00 €</b></div></div>
<div id="ah"></div>""", js="""
const num=v=>{v=String(v||'').replace(',','.').replace(/[^0-9.]/g,'');return parseFloat(v)||0};
let S=[];
function draw(){const L=$('#lista');L.innerHTML='';S.forEach((s,i)=>{const d=document.createElement('div');d.className='it'+(s.on?'':' off');d.innerHTML='<span class="ck">'+(s.on?'✓':'')+'</span><span class="n"></span><b class="p">'+eur(s.c)+'</b>';d.querySelector('.n').textContent=s.n;d.querySelector('.ck').addEventListener('click',()=>{s.on=!s.on;draw()});L.appendChild(d)});
const m=S.filter(s=>s.on).reduce((a,s)=>a+s.c,0),all=S.reduce((a,s)=>a+s.c,0);$('#mes').textContent=eur(m);$('#anio').textContent=eur(m*12);
const ah=(all-m)*12;$('#ah').textContent=ah>0?'Ahorras '+eur(ah)+' al año':''}
$('#add').addEventListener('click',()=>{const c=Math.round(num($('#pre').value)*100);if(!$('#nom').value.trim()||!c)return;S.push({n:$('#nom').value.trim(),c:c,on:true});$('#nom').value='';$('#pre').value='';draw()});
window.reset=()=>{S=[];$('#nom').value='';$('#pre').value='';draw()};
window.preset=()=>{S=[{n:'Streaming',c:1299,on:true},{n:'Música',c:1099,on:true},{n:'Gimnasio',c:2990,on:true}];draw()};
window.reset();
""")

# ---------------------------------------------------------------- 4. compra
T["compra"] = dict(titulo="Lista de la compra", css="""
textarea{font-size:40px;min-height:230px;resize:none;line-height:1.35}
.g{margin-bottom:8px}
.g h3{font-size:28px;color:var(--accd);text-transform:uppercase;letter-spacing:.06em;margin-bottom:2px}
.i{display:flex;align-items:center;gap:18px;font-size:36px;padding:2px 0}
.ck{width:46px;height:46px;border-radius:14px;border:4px solid var(--acc);background:var(--acc);color:#fff;text-align:center;font-weight:700;line-height:36px;font-size:30px}
.i.off .ck{background:#fff}.i.off .t{text-decoration:line-through;color:var(--mut)}
""", body="""
<h2>Lista de la compra</h2>
<div id="ed"><label>Pega tu lista</label><textarea id="txt" placeholder="leche, pan, detergente…"></textarea>
<button id="ord" style="width:100%;margin-top:22px">Ordenar por secciones</button></div>
<div id="out" style="display:none"></div>""", js="""
const SEC=[['Frutas y verduras',['manzana','platan','naranja','tomate','lechuga','patata','cebolla','zanahoria','limon','pera','fresa','pimiento','aguacate','uva']],
['Lácteos y huevos',['leche','yogur','queso','mantequilla','huevo','nata']],['Panadería',['pan','bollo','tostada']],
['Carne y pescado',['pollo','carne','jamon','pescado','atun','salmon']],['Despensa',['arroz','pasta','aceite','azucar','cafe','galleta','harina','lenteja','sal','cereal']],
['Limpieza e higiene',['detergente','lejia','papel higienico','fregasuelos','jabon','champu','suavizante','estropajo','bolsas de basura']]];
const norm=s=>s.toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').trim();
function sec(it){const n=norm(it);for(const [t,k] of SEC){if(k.some(w=>n===w||n.startsWith(w)))return t}return 'Otros'}
function ordenar(){const items=$('#txt').value.split(/[\\n,;]+/).map(s=>s.trim()).filter(Boolean);if(!items.length)return;
const G={};items.forEach(i=>{(G[sec(i)]=G[sec(i)]||[]).push(i)});const o=$('#out');o.innerHTML='';
[...SEC.map(s=>s[0]),'Otros'].filter(t=>G[t]).forEach(t=>{const g=document.createElement('div');g.className='g';g.innerHTML='<h3>'+t+'</h3>';G[t].forEach(i=>{const d=document.createElement('div');d.className='i';d.innerHTML='<span class="ck"></span><span class="t"></span>';d.querySelector('.t').textContent=i.charAt(0).toUpperCase()+i.slice(1);d.addEventListener('click',()=>{d.classList.toggle('off');d.querySelector('.ck').textContent=d.classList.contains('off')?'':'✓'});d.querySelector('.ck').textContent='✓';g.appendChild(d)});o.appendChild(g)});
$('#ed').style.display='none';o.style.display='block'}
$('#ord').addEventListener('click',ordenar);
window.reset=()=>{$('#txt').value='';$('#ed').style.display='block';$('#out').style.display='none'};
window.preset=()=>{$('#txt').value='leche, papel higiénico, manzanas, pan, detergente, yogures, tomates, arroz, lejía, huevos';ordenar()};
window.reset();
""")


# ---------------------------------------------------------------- 5. plato (hosteleria)
T["plato"] = dict(titulo="Coste del plato", css="""
.ln{display:grid;grid-template-columns:1fr 210px;gap:14px;margin-bottom:14px}
.ln input{font-size:36px;padding:14px 18px}
.hd{display:grid;grid-template-columns:1fr 210px;gap:14px;font-size:28px;color:var(--mut);margin-bottom:8px}
.step{display:flex;align-items:center;justify-content:space-between;background:#F3F7F9;border-radius:26px;padding:10px 18px}
.step button{width:84px;height:84px;padding:0;font-size:54px;line-height:1}
.step b{font-size:58px}
.chips{display:flex;gap:14px}.chips button{flex:1;background:#EAF0F3;color:var(--ink);padding:16px 0}.chips button.on{background:var(--acc);color:#fff}
.res{display:flex;gap:18px;margin-top:26px}.res div{flex:1;background:#EAF7FA;border-radius:30px;padding:24px;text-align:center}
.res span{display:block;font-size:28px;color:var(--mut)}.res b{font-size:62px;color:var(--accd)}
""", body="""
<h2>Coste del plato</h2>
<div class="hd"><span>Ingrediente</span><span>Coste €</span></div>
<div id="lines"></div>
<button class="sec" id="add" style="font-size:32px;padding:12px 26px;margin-bottom:22px">+ Ingrediente</button>
<div class="row" style="gap:22px;margin-bottom:18px"><div style="flex:1"><label>Raciones</label><div class="step"><button class="sec" id="men">−</button><b id="rac">1</b><button id="mas">+</button></div></div>
<div style="flex:1"><label>Coste objetivo</label><div class="chips" id="chips"><button data-p="30" class="on">30 %</button><button data-p="35">35 %</button></div></div></div>
<div class="res"><div><span>Coste por ración</span><b id="cr">0,00 €</b></div><div><span>Vender a (sin IVA)</span><b id="pv">0,00 €</b></div></div>""", js="""
const num=v=>{v=String(v||'').replace(',','.').replace(/[^0-9.]/g,'');return parseFloat(v)||0};
let R=1,OBJ=30;
function addLine(n,c){const d=document.createElement('div');d.className='ln';d.innerHTML='<input placeholder="Ingrediente" value="'+(n||'')+'"><input inputmode="decimal" placeholder="0,00" value="'+(c||'')+'">';d.querySelectorAll('input').forEach(i=>i.addEventListener('input',calc));$('#lines').appendChild(d);calc()}
function calc(){let t=0;document.querySelectorAll('.ln').forEach(l=>{t+=Math.round(num(l.querySelectorAll('input')[1].value)*100)});
const cr=Math.round(t/R);$('#rac').textContent=R;$('#cr').textContent=eur(cr);$('#pv').textContent=eur(Math.round(cr*100/OBJ));
document.querySelectorAll('#chips button').forEach(b=>b.classList.toggle('on',+b.dataset.p===OBJ))}
$('#add').addEventListener('click',()=>addLine());$('#mas').addEventListener('click',()=>{R=Math.min(40,R+1);calc()});$('#men').addEventListener('click',()=>{R=Math.max(1,R-1);calc()});
document.querySelectorAll('#chips button').forEach(b=>b.addEventListener('click',()=>{OBJ=+b.dataset.p;calc()}));
window.reset=()=>{$('#lines').innerHTML='';R=1;OBJ=30;addLine();addLine();addLine()};
window.preset=()=>{$('#lines').innerHTML='';R=4;OBJ=30;addLine('Huevos','2,40');addLine('Patatas','1,20');addLine('Cebolla','0,40');addLine('Aceite','0,80')};
window.reset();
""")

# ---------------------------------------------------------------- 6. pedidos (tienda pequena)
T["pedidos"] = dict(titulo="Mis pedidos", css="""
.f{display:grid;grid-template-columns:260px 1fr;gap:14px;margin-bottom:14px}
.f input{font-size:38px}
.it{display:flex;align-items:center;gap:18px;background:#F3F7F9;border-radius:24px;padding:18px 24px;margin-bottom:12px;font-size:38px}
.it .n{flex:1;font-weight:500}.it .n small{display:block;font-size:28px;color:var(--mut);font-weight:400}
.st{border:0;border-radius:40px;padding:10px 26px;font-size:30px;font-weight:700;color:#fff;min-width:220px;text-align:center}
.s0{background:#E8A33D}.s1{background:var(--acc)}.s2{background:#3DAA6D}
.sum{display:flex;gap:14px;margin-top:18px}.sum div{flex:1;background:#EAF7FA;border-radius:26px;padding:18px;text-align:center}
.sum span{display:block;font-size:26px;color:var(--mut)}.sum b{font-size:58px;color:var(--accd)}
""", body="""
<h2>Mis pedidos</h2>
<div class="f"><input id="cli" placeholder="Cliente"><input id="art" placeholder="Qué ha pedido"></div>
<button id="add" style="width:100%;margin-bottom:20px">Añadir pedido</button>
<div id="lista" style="min-height:330px"></div>
<div class="sum"><div><span>Pendientes</span><b id="c0">0</b></div><div><span>Hechos</span><b id="c1">0</b></div><div><span>Entregados</span><b id="c2">0</b></div></div>""", js="""
const ET=['Pendiente','Hecho','Entregado'];let P=[];
function draw(){const L=$('#lista');L.innerHTML='';P.forEach((p,i)=>{const d=document.createElement('div');d.className='it';d.innerHTML='<span class="n"><span class="nm"></span><small class="ar"></small></span><button class="st s'+p.e+'">'+ET[p.e]+'</button>';d.querySelector('.nm').textContent=p.c;d.querySelector('.ar').textContent=p.a;d.querySelector('.st').addEventListener('click',()=>{p.e=(p.e+1)%3;draw()});L.appendChild(d)});
for(let k=0;k<3;k++)$('#c'+k).textContent=P.filter(p=>p.e===k).length}
$('#add').addEventListener('click',()=>{if(!$('#cli').value.trim()||!$('#art').value.trim())return;P.push({c:$('#cli').value.trim(),a:$('#art').value.trim(),e:0});$('#cli').value='';$('#art').value='';draw()});
window.reset=()=>{P=[];$('#cli').value='';$('#art').value='';draw()};
window.preset=()=>{P=[{c:'Marta',a:'Taza con nombre',e:2},{c:'Luis',a:'Llavero de madera',e:1},{c:'Ana',a:'Caja de regalo',e:0}];draw()};
window.reset();
""")

# ---------------------------------------------------------------- 7. citas (familia)
T["citas"] = dict(titulo="Citas de la familia", css="""
.hoy{font-size:30px;color:var(--mut);margin:-14px 0 20px}
.f{display:grid;grid-template-columns:1fr 170px;gap:14px;margin-bottom:14px}
.f input{font-size:38px}
.it{display:flex;align-items:center;gap:18px;background:#F3F7F9;border-radius:24px;padding:20px 26px;margin-bottom:12px;font-size:40px}
.it .d{min-width:130px;text-align:center;background:#fff;border:3px solid var(--line);border-radius:20px;padding:6px 0;font-weight:700;color:var(--accd);font-size:34px;line-height:1.1}
.it .d small{display:block;font-size:22px;color:var(--mut);font-weight:500}
.it .n{flex:1;font-weight:500}
.it .m{background:var(--acc);color:#fff;font-size:26px;font-weight:700;border-radius:30px;padding:8px 20px}
.it.man{background:#EAF7FA;border:3px solid var(--acc)}
""", body="""
<h2>Citas de la familia</h2>
<div class="hoy">Hoy: 11 de noviembre</div>
<div class="f"><input id="txt" placeholder="Quién y qué cita"><input id="dia" inputmode="numeric" placeholder="Día"></div>
<button id="add" style="width:100%;margin-bottom:20px">Apuntar cita</button>
<div id="lista" style="min-height:380px"></div>""", js="""
const HOY=11;let C=[];
function draw(){const L=$('#lista');L.innerHTML='';C.slice().sort((a,b)=>a.d-b.d).forEach(c=>{const man=c.d===HOY+1;const d=document.createElement('div');d.className='it'+(man?' man':'');d.innerHTML='<span class="d"><small>nov</small>'+c.d+'</span><span class="n"></span>'+(man?'<span class="m">MAÑANA</span>':'');d.querySelector('.n').textContent=c.t;L.appendChild(d)})}
$('#add').addEventListener('click',()=>{const d=parseInt($('#dia').value,10);if(!$('#txt').value.trim()||!(d>=1&&d<=30))return;C.push({t:$('#txt').value.trim(),d:d});$('#txt').value='';$('#dia').value='';draw()});
window.reset=()=>{C=[];$('#txt').value='';$('#dia').value='';draw()};
window.preset=()=>{C=[{t:'Abuela: dentista',d:12},{t:'Mamá: revisión del coche',d:15},{t:'Abuelo: peluquería',d:18}];draw()};
window.reset();
""")

# ---------------------------------------------------------------- 8. semana (creadores)
T["semana"] = dict(titulo="Mi semana de contenido", css="""
.dia{display:grid;grid-template-columns:110px 1fr 70px;gap:14px;align-items:center;margin-bottom:10px}
.dia b{font-size:34px;color:var(--accd)}
.dia input{font-size:34px;padding:12px 18px}
.ck{width:62px;height:62px;border-radius:18px;border:4px solid var(--line);background:#fff;color:#fff;font-size:42px;line-height:54px;text-align:center;font-weight:700}
.ck.on{background:var(--acc);border-color:var(--acc)}
.sum{display:flex;gap:16px;margin-top:20px}.sum div{flex:1;background:#EAF7FA;border-radius:26px;padding:18px;text-align:center}
.sum span{display:block;font-size:26px;color:var(--mut)}.sum b{font-size:56px;color:var(--accd)}
""", body="""
<h2>Mi semana de contenido</h2>
<div id="dias"></div>
<div class="sum"><div><span>Planificados</span><b id="pl">0</b></div><div><span>Publicados</span><b id="pu">0</b></div><div><span>Días libres</span><b id="li">7</b></div></div>""", js="""
const D=['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'];let OK=[0,0,0,0,0,0,0];
function calc(){const ins=document.querySelectorAll('.dia input');let pl=0,pu=0;ins.forEach((i,k)=>{const t=i.value.trim()!=='';if(t)pl++;if(t&&OK[k])pu++;document.querySelectorAll('.ck')[k].classList.toggle('on',!!OK[k]);document.querySelectorAll('.ck')[k].textContent=OK[k]?'✓':''});
$('#pl').textContent=pl;$('#pu').textContent=pu;$('#li').textContent=7-pl}
function build(v){const w=$('#dias');w.innerHTML='';D.forEach((n,k)=>{const d=document.createElement('div');d.className='dia';d.innerHTML='<b>'+n+'</b><input placeholder="Idea del día" value="'+((v&&v[k])||'')+'"><span class="ck"></span>';d.querySelector('input').addEventListener('input',calc);d.querySelector('.ck').addEventListener('click',()=>{OK[k]=OK[k]?0:1;calc()});w.appendChild(d)});calc()}
window.reset=()=>{OK=[0,0,0,0,0,0,0];build()};
window.preset=()=>{OK=[1,0,1,0,0,0,0];build(['Truco rápido','','Detrás de cámaras','Pregunta a la comunidad'])};
window.reset();
""")

for k, v in T.items():
    h = base.replace("__TITULO__", v["titulo"]).replace("__CSS__", v["css"]).replace("__BODY__", v["body"]).replace("__JS__", v["js"])
    open(os.path.join(HERE, k + ".html"), "w", encoding="utf-8").write(h)
    print("ok", k, len(h))
