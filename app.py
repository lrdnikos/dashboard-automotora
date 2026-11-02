import csv
import io

from flask import Flask, Response, render_template_string

app = Flask(__name__)

# Referencias del caso y metas académicas.
DATOS = [
    {
        "id": "postventa",
        "nombre": "Ingresos de postventa",
        "categoria": "Finanzas",
        "valor": 3.5,
        "meta": 3.7,
        "unidad": "M USD",
        "operador": "≥",
        "texto": "US$ 3,5 M",
        "meta_texto": "≥ US$ 3,7 M",
        "contexto": "Ventas mensuales aproximadas del caso",
        "plazo": "Meta mensual 2027",
        "accion": "Revisar capacidad del taller, retención de clientes y oportunidades de servicio.",
    },
    {
        "id": "repuestos",
        "nombre": "Margen de repuestos",
        "categoria": "Finanzas",
        "valor": 40,
        "meta": 40,
        "unidad": "%",
        "operador": "≥",
        "texto": "40%",
        "meta_texto": "≥ 40%",
        "contexto": "Margen promedio indicado en el caso",
        "plazo": "Meta de protección",
        "accion": "Controlar descuentos, costos de compra y mezcla de repuestos vendidos.",
    },
    {
        "id": "vehiculos",
        "nombre": "Margen de vehículos nuevos",
        "categoria": "Finanzas",
        "valor": 12,
        "meta": 12,
        "unidad": "%",
        "operador": "≥",
        "texto": "12%",
        "meta_texto": "≥ 12%",
        "contexto": "Margen promedio indicado en el caso",
        "plazo": "Meta de protección",
        "accion": "Evaluar promociones y descuentos para proteger la rentabilidad.",
    },
    {
        "id": "mercado",
        "nombre": "Participación de mercado",
        "categoria": "Clientes",
        "valor": 10.08,
        "meta": 11,
        "unidad": "%",
        "operador": "≥",
        "texto": "10,08%",
        "meta_texto": "≥ 11%",
        "contexto": "Participación indicada en el caso",
        "plazo": "Meta al cierre de 2027",
        "accion": "Mejorar captación de clientes y conversión comercial.",
    },
    {
        "id": "respuesta",
        "nombre": "Respuesta a cotizaciones web",
        "categoria": "Procesos",
        "valor": 48,
        "meta": 2,
        "unidad": "h",
        "operador": "≤",
        "texto": "48 h",
        "meta_texto": "≤ 2 h",
        "contexto": "Plazo máximo actual indicado en el caso",
        "plazo": "Meta a 12 meses",
        "accion": "Asignar responsables, alertas y seguimiento de las consultas web.",
    },
    {
        "id": "stock",
        "nombre": "Disponibilidad de stock solicitado",
        "categoria": "Clientes",
        "valor": None,
        "meta": 95,
        "unidad": "%",
        "operador": ">",
        "texto": "Por medir",
        "meta_texto": "> 95%",
        "contexto": "El caso no informa una medición actual",
        "plazo": "Estándar del caso",
        "accion": "Medir las solicitudes atendidas con stock disponible y documentar su cálculo.",
    },
]


def obtener_estado(item):
    if item["valor"] is None:
        return "pendiente"

    if item["operador"] == "≤":
        cumple = item["valor"] <= item["meta"]
    elif item["operador"] == ">":
        cumple = item["valor"] > item["meta"]
    else:
        cumple = item["valor"] >= item["meta"]

    return "umbral" if cumple else "brecha"


for indicador in DATOS:
    indicador["estado"] = obtener_estado(indicador)


PAGINA = r"""
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Dashboard estratégico de Automotora Viña del Mar">
<title>AVDM · Dashboard estratégico</title>
<style>
:root{
  --fondo:#f4f7fa;--papel:#fff;--texto:#172d3e;
  --muted:#6d8090;--linea:#e2e9ef;--verde:#087f72;
  --verde-claro:#e8f6f1;--ambar:#af6d18;
  --ambar-claro:#fff4e2;--gris:#91a4b5;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--fondo);color:var(--texto);
  font-family:Inter,"Segoe UI",Arial,sans-serif;font-size:14px}
button,input,select{font:inherit}
button,a,select{touch-action:manipulation}
button{cursor:pointer;color:inherit}
a{color:inherit;text-decoration:none}
h1,h2,h3,p{margin:0}
button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible{
  outline:3px solid #42b4a1;outline-offset:3px}
[hidden]{display:none!important}
.sidebar{position:fixed;inset:0 auto 0 0;width:220px;background:white;
  border-right:1px solid var(--linea);padding:30px 20px;
  display:flex;flex-direction:column}
.brand{display:flex;align-items:center;gap:11px;font-size:24px;font-weight:800}
.logo{background:var(--verde);color:white;border-radius:12px;
  width:43px;height:43px;display:grid;place-items:center;font-size:27px}
.brand small{display:block;font-size:8px;letter-spacing:1.8px;
  color:var(--muted);margin-top:5px}
.nav-title{font-size:9px;letter-spacing:1.5px;color:var(--muted);margin:44px 10px 15px}
nav{display:grid;gap:8px}
nav a{padding:13px 12px;border-radius:9px;color:var(--muted);font-size:12px}
nav a:hover,nav a:first-child{color:var(--verde);background:var(--verde-claro)}
.sidebar-bottom{margin-top:auto;border-top:1px solid var(--linea);
  padding:20px 8px 0;font-size:11px;line-height:1.8}
.sidebar-bottom p{color:var(--muted);font-size:10px}
.sidebar-bottom span{display:inline-block;font-size:8px;margin-top:12px;
  background:#eef3f6;padding:5px 8px;border-radius:5px;letter-spacing:1px}
.workspace{margin-left:220px}
.topbar{display:flex;justify-content:space-between;align-items:center;
  height:72px;padding:0 35px;border-bottom:1px solid var(--linea);
  background:#fff;font-size:11px;color:var(--muted)}
.topbar strong{color:var(--texto)}
.badge{background:#edf5f2;color:var(--verde);padding:7px 11px;
  border-radius:20px;font-size:10px}
main{max-width:1500px;padding:35px;margin:auto}
.hero{display:flex;justify-content:space-between;gap:22px;align-items:center}
.eyebrow{font-size:9px;letter-spacing:1.7px;font-weight:700;
  color:var(--verde);margin-bottom:10px;text-transform:uppercase}
h1{font-size:clamp(26px,3vw,39px);letter-spacing:-1.7px;line-height:1.15}
h1 span{color:var(--verde)}
.subtitle{color:var(--muted);font-size:12px;margin-top:12px;line-height:1.7}
.actions{display:flex;gap:8px;flex-wrap:wrap}
.button{display:inline-flex;align-items:center;justify-content:center;
  gap:8px;border:1px solid var(--linea);border-radius:8px;background:white;
  padding:11px 15px;font-size:11px;font-weight:600;white-space:nowrap}
.button:hover{background:#edf5f2}
.button.primary{background:var(--verde);border-color:var(--verde);color:white}
.notice{margin:25px 0;background:#eaf1f4;border:1px solid #dce7ec;
  color:#597280;border-radius:9px;padding:13px 16px;font-size:11px;line-height:1.8}
.summary{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:15px}
.summary-card{background:white;border:1px solid var(--linea);
  padding:20px;border-radius:12px}
.summary-card span{font-size:9px;letter-spacing:1px;color:var(--muted)}
.summary-card strong{display:block;font-size:36px;letter-spacing:-1.5px;margin:13px 0 8px}
.summary-card p{font-size:10px;color:var(--muted);line-height:1.6}
section{scroll-margin-top:25px}
.section-head{display:flex;align-items:end;justify-content:space-between;
  gap:20px;margin:34px 0 18px}
.section-head h2{font-size:21px;letter-spacing:-.7px}
.section-head p{font-size:10px;color:var(--muted)}
.chart-grid{display:grid;grid-template-columns:.9fr 1.3fr;gap:18px}
.panel{background:white;border:1px solid var(--linea);border-radius:13px;padding:23px;min-width:0}
.panel h3{font-size:16px;letter-spacing:-.4px}
.panel-sub{font-size:10px;color:var(--muted);line-height:1.7;margin-top:8px}
.donut-wrap{display:flex;align-items:center;justify-content:center;gap:20px;margin-top:20px}
.donut{width:190px;max-width:50%;flex-shrink:0}
.donut svg{width:100%;height:auto;display:block}
.legend{display:grid;gap:10px}
.legend button{border:0;background:#f7f9fb;text-align:left;padding:9px 10px;
  border-radius:7px;font-size:10px;display:flex;align-items:center;gap:8px}
.legend button:hover{background:#eaf2f0}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;flex-shrink:0}
.legend strong{margin-left:5px}
.donut-note{font-size:9px;color:var(--muted);line-height:1.7;margin-top:18px}
.bar-svg{width:100%;display:block;height:auto;margin-top:17px}
.chart-legend{display:flex;justify-content:center;gap:18px;font-size:10px;
  color:var(--muted);margin-top:7px}
.chart-legend span{display:flex;align-items:center;gap:6px}
.chart-legend i{width:10px;height:10px;border-radius:3px;display:inline-block}
.toolbar{display:flex;justify-content:space-between;gap:15px;flex-wrap:wrap}
.tabs{display:flex;gap:4px;background:#e8eef2;padding:4px;border-radius:8px}
.tab{border:0;background:transparent;padding:9px 13px;border-radius:5px;
  font-size:11px;color:var(--muted)}
.tab.active{background:white;color:var(--verde);box-shadow:0 1px 4px #17354710}
.inputs{display:flex;gap:8px}
input,select{border:1px solid var(--linea);background:white;border-radius:7px;
  padding:10px 11px;color:var(--texto);font-size:11px;max-width:100%}
input{width:190px}
.result-line{display:flex;align-items:center;gap:12px;color:var(--muted);
  font-size:10px;margin:15px 0}
.text-button{border:0;background:transparent;color:var(--verde);
  font-size:10px;text-decoration:underline}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:15px}
.card{background:white;border:1px solid var(--linea);padding:21px;
  border-radius:12px;text-align:left;display:flex;flex-direction:column;
  min-height:245px;position:relative;transition:transform .18s,box-shadow .18s}
.card:hover{transform:translateY(-3px);box-shadow:0 10px 26px #183f4e0d;border-color:#a5cec4}
.category{font-size:9px;color:var(--verde);letter-spacing:1.2px;text-transform:uppercase}
.card-arrow{position:absolute;right:20px;top:16px;color:#9baeb9;font-size:19px}
.card h3{font-size:12px;line-height:1.5;margin:15px 0;min-height:36px;padding-right:10px}
.value{font-size:32px;font-weight:750;letter-spacing:-1px}
.value.pending{font-size:27px;color:#8596a4}
.context{font-size:10px;color:var(--muted);line-height:1.6;margin:9px 0 20px}
.card-bottom{margin-top:auto;padding-top:13px;border-top:1px solid #edf1f5;
  display:flex;justify-content:space-between;align-items:end;gap:8px;flex-wrap:wrap}
.target{font-size:9px;color:var(--muted);line-height:1.7}
.target strong{display:block;font-size:12px;color:var(--texto)}
.status{font-size:9px;border-radius:5px;padding:5px 7px;white-space:nowrap}
.status.umbral{background:var(--verde-claro);color:var(--verde)}
.status.brecha{background:var(--ambar-claro);color:var(--ambar)}
.status.pendiente{background:#edf2f7;color:#74899b}
.empty{padding:35px;text-align:center;border:1px dashed var(--linea);
  border-radius:12px;background:white;color:var(--muted);font-size:12px}
.comparison-layout{display:grid;grid-template-columns:1.2fr 1fr;gap:25px;margin-top:22px}
.comparison-select{width:100%;margin-bottom:22px}
.bar-row{margin-bottom:20px}
.bar-label{display:flex;justify-content:space-between;gap:15px;font-size:11px;margin-bottom:9px}
.bar-label span{color:var(--muted)}
.track{height:17px;background:#f0f4f6;border-radius:4px;overflow:hidden}
.fill{height:100%;border-radius:4px;background:var(--verde);min-width:3px}
.fill.goal{background:#a2cfc4}
.gap{background:var(--verde-claro);color:#346e60;padding:13px;border-radius:8px;
  font-size:11px;line-height:1.7}
.action-panel{background:#f7fafb;border:1px solid var(--linea);
  border-radius:10px;padding:20px}
.action-panel p{font-size:12px;line-height:1.8;color:#58717f}
.action-panel h4{font-size:13px;margin:0 0 12px}
.action-panel small{display:block;margin-top:18px;font-size:10px;color:var(--muted)}
footer{display:flex;justify-content:space-between;gap:20px;margin-top:28px;
  padding:20px 0 0;border-top:1px solid var(--linea);color:var(--muted);
  font-size:9px;line-height:1.8}
footer p:last-child{text-align:right}
dialog{border:1px solid var(--linea);border-radius:16px;padding:27px;
  width:calc(100% - 30px);max-width:510px;max-height:90dvh;
  overflow:auto;color:var(--texto);box-shadow:0 25px 90px #183b4430}
dialog::backdrop{background:#15374877;backdrop-filter:blur(4px)}
.modal-close{float:right}
.modal-close button{border:0;border-radius:50%;background:#eef3f5;
  width:32px;height:32px;font-size:22px}
dialog h2{font-size:24px;line-height:1.3;letter-spacing:-.7px;margin:15px 0}
.modal-values{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:22px 0}
.modal-values div{background:#f3f7f8;padding:15px;border-radius:9px}
.modal-values small{font-size:9px;color:var(--muted);display:block;line-height:1.7}
.modal-values strong{font-size:25px;display:block;margin-top:8px}
.modal-action{font-size:12px;line-height:1.8;margin-top:18px;color:#58717f}
.modal-note{font-size:9px;color:var(--muted);line-height:1.8;margin-top:18px}
@media(max-width:1150px){
  .sidebar{width:190px;padding:28px 15px}.workspace{margin-left:190px}
  main{padding:27px}.topbar{padding:0 27px}.hero{flex-wrap:wrap}
  .chart-grid{grid-template-columns:1fr 1.3fr}
  .donut-wrap{flex-direction:column;gap:12px}.donut{max-width:100%;width:170px}
  .legend{width:100%;gap:6px}.legend button{justify-content:space-between}
  .value{font-size:28px}.summary-card{padding:17px}
}
@media(max-width:850px){
  .sidebar{display:none}.workspace{margin-left:0}
  .summary{grid-template-columns:repeat(2,minmax(0,1fr))}
  .cards{grid-template-columns:repeat(2,minmax(0,1fr))}
  .comparison-layout{grid-template-columns:1fr}
  .chart-grid{grid-template-columns:1fr 1.2fr}
  .panel{padding:18px}.section-head p{display:none}
}
@media(max-width:580px){
  main{padding:23px 15px}.topbar{height:58px;padding:0 15px;font-size:9px}
  .badge{font-size:8px}.hero h1{font-size:29px}
  .hero .eyebrow{font-size:8px}.subtitle{font-size:11px}
  .actions{width:100%}.button{font-size:10px;padding:10px 13px}
  .notice{font-size:10px;padding:12px}
  .summary{gap:10px}.summary-card{padding:15px}
  .summary-card span{font-size:7px}.summary-card strong{font-size:30px}
  .summary-card p{font-size:9px}
  .chart-grid{grid-template-columns:1fr}
  .donut-wrap{flex-direction:row}.donut{width:160px;max-width:47%}
  .legend{width:auto}.legend button{font-size:9px}
  .section-head h2{font-size:19px}
  .toolbar,.inputs{width:100%}.inputs input{width:52%;min-width:0}
  .inputs select{width:48%}.tabs{width:100%;justify-content:space-between}
  .tab{font-size:10px;padding:9px 11px}
  .cards{gap:10px}.card{padding:15px 12px;min-height:255px}
  .card h3{font-size:11px;min-height:46px}.category{font-size:8px}
  .card-arrow{right:11px;top:11px}.value{font-size:25px}
  .value.pending{font-size:22px}.context{font-size:9px}
  .status{font-size:8px}.target{font-size:8px}.target strong{font-size:11px}
  .bar-label{font-size:10px}.panel h3{font-size:15px}
  footer{font-size:8px}.modal-values strong{font-size:23px}
}
@media(max-width:350px){.cards{grid-template-columns:1fr}.card{min-height:220px}}
@media(prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}*{transition:none!important}
}
@media print{
  @page{size:A4;margin:10mm}
  body{background:white;print-color-adjust:exact;-webkit-print-color-adjust:exact}
  .sidebar,.topbar,.actions,.toolbar,.result-line,.card-arrow,dialog{display:none!important}
  .workspace{margin:0}main{padding:0}
  .summary{grid-template-columns:repeat(4,1fr);gap:8px}
  .summary-card{padding:12px}.summary-card strong{font-size:26px}
  .summary-card span{font-size:6px}.summary-card p{font-size:8px}
  .chart-grid{grid-template-columns:1fr 1.3fr}
  .cards{grid-template-columns:repeat(3,1fr);gap:9px}
  .card{break-inside:avoid;min-height:225px;padding:13px}
  .value{font-size:25px}.context{font-size:8px}
  .panel{padding:15px;break-inside:avoid}
  .comparison-select{display:none}.comparison-layout{grid-template-columns:1fr 1fr}
  h1{font-size:29px}.notice{font-size:9px}.section-head{margin-top:22px}
  .legend button{font-size:8px}.donut{width:130px}
}
</style>
</head>
<body>
<aside class="sidebar">
  <a class="brand" href="#inicio">
    <span class="logo">A</span>
    <span>AVDM<small>CONTROL DE GESTIÓN</small></span>
  </a>
  <p class="nav-title">ESPACIO DE TRABAJO</p>
  <nav aria-label="Navegación principal">
    <a href="#inicio">▦ &nbsp; Vista general</a>
    <a href="#graficos">◉ &nbsp; Gráficos</a>
    <a href="#indicadores">◫ &nbsp; Indicadores</a>
    <a href="#comparativo">↗ &nbsp; Comparar metas</a>
  </nav>
  <div class="sidebar-bottom">
    <strong>Automotora Viña del Mar</strong>
    <p>Estrategia y desempeño</p>
    <span>CASO ACADÉMICO · 2027</span>
  </div>
</aside>

<div class="workspace">
  <header class="topbar">
    <span>Control de gestión &nbsp; / &nbsp; <strong>Dashboard estratégico</strong></span>
    <span class="badge">Referencias del caso</span>
  </header>

  <main>
    <section class="hero" id="inicio">
      <div>
        <p class="eyebrow">AUTOMOTORA VIÑA DEL MAR S.A.C.</p>
        <h1>El negocio, en perspectiva<span>.</span></h1>
        <p class="subtitle">Crecimiento rentable, servicio ágil y disponibilidad.</p>
      </div>
      <div class="actions">
        <button class="button" id="imprimir" type="button">↗ Imprimir</button>
        <a class="button primary" href="{{ url_for('descargar') }}">↓ Descargar CSV</a>
      </div>
    </section>

    <div class="notice">
      <strong>Contexto de lectura.</strong>
      Las cifras son referencias del caso. Las metas 2027 son propuestas académicas;
      el estándar de stock proviene del caso. No hay actualización automática de datos.
    </div>

    <section class="summary" aria-label="Resumen de indicadores">
      <div class="summary-card">
        <span>INDICADORES ESTRATÉGICOS</span>
        <strong id="total"></strong>
        <p>3 financieros · 3 no financieros</p>
      </div>
      <div class="summary-card">
        <span>REFERENCIAS EN UMBRAL</span>
        <strong id="total-umbral" style="color:var(--verde)"></strong>
        <p>Referencias que alcanzan el umbral</p>
      </div>
      <div class="summary-card">
        <span>BRECHAS FRENTE A META</span>
        <strong id="total-brecha" style="color:var(--ambar)"></strong>
        <p>Oportunidades de mejora</p>
      </div>
      <div class="summary-card">
        <span>MEDICIÓN PENDIENTE</span>
        <strong id="total-pendiente"></strong>
        <p>Indicadores sin referencia medida</p>
      </div>
    </section>

    <section id="graficos">
      <div class="section-head">
        <div>
          <p class="eyebrow">PANORAMA VISUAL</p>
          <h2>Tres formas de entender el desempeño</h2>
        </div>
        <p>Vista completa del caso</p>
      </div>
      <div class="chart-grid">
        <article class="panel">
          <h3>Distribución de indicadores</h3>
          <p class="panel-sub">Cantidad de indicadores según su comparación con la meta.</p>
          <div class="donut-wrap">
            <div id="torta" class="donut"></div>
            <div id="leyenda-torta" class="legend"></div>
          </div>
          <p class="donut-note">
            Selecciona un estado en la leyenda para filtrar las tarjetas.
            La torta cuenta indicadores; no suma ingresos, horas ni porcentajes.
          </p>
        </article>

        <article class="panel">
          <h3>Márgenes y participación</h3>
          <p class="panel-sub">
            Referencias y metas de los tres indicadores con medición expresada en porcentaje.
          </p>
          <div id="barras"></div>
          <div class="chart-legend">
            <span><i style="background:#087f72"></i>Referencia del caso</span>
            <span><i style="background:#a2cfc4"></i>Meta propuesta</span>
          </div>
          <p class="donut-note">
            Son indicadores distintos: las barras comparan cada referencia con su propia meta.
          </p>
        </article>
      </div>
    </section>

    <section id="indicadores">
      <div class="section-head">
        <div>
          <p class="eyebrow">CUADRO DE MANDO</p>
          <h2>Los indicadores que importan</h2>
        </div>
        <p>Selecciona una tarjeta para ver el detalle ↗</p>
      </div>

      <div class="toolbar">
        <div class="tabs" role="group" aria-label="Filtrar por perspectiva">
          <button class="tab active" data-categoria="Todas" aria-pressed="true">Todos</button>
          <button class="tab" data-categoria="Finanzas" aria-pressed="false">Finanzas</button>
          <button class="tab" data-categoria="Clientes" aria-pressed="false">Clientes</button>
          <button class="tab" data-categoria="Procesos" aria-pressed="false">Procesos</button>
        </div>
        <div class="inputs">
          <input id="buscar" type="search" aria-label="Buscar indicador"
                 placeholder="Buscar indicador…">
          <select id="filtro-estado" aria-label="Filtrar por estado">
            <option value="todos">Todos los estados</option>
            <option value="umbral">En umbral</option>
            <option value="brecha">Con brecha</option>
            <option value="pendiente">Sin medición</option>
          </select>
        </div>
      </div>

      <div class="result-line" aria-live="polite">
        <span id="resultados"></span>
        <button id="limpiar" class="text-button" hidden>Limpiar filtros</button>
      </div>
      <div id="tarjetas" class="cards"></div>
      <div id="vacio" class="empty" hidden>
        No encontramos indicadores. Prueba otra búsqueda o limpia los filtros.
      </div>
    </section>

    <section id="comparativo">
      <div class="section-head">
        <div>
          <p class="eyebrow">REFERENCIA VS. OBJETIVO</p>
          <h2>La distancia a la meta</h2>
        </div>
        <p>Comparación individual</p>
      </div>

      <article class="panel">
        <label for="comparar" class="panel-sub">Selecciona un indicador</label>
        <select id="comparar" class="comparison-select">
          {% for item in datos %}
          <option value="{{ item.id }}">{{ item.nombre }}</option>
          {% endfor %}
        </select>
        <div class="comparison-layout">
          <div id="comparacion" aria-live="polite"></div>
          <div class="action-panel">
            <p class="eyebrow">ACCIÓN SUGERIDA</p>
            <h4 id="accion-titulo"></h4>
            <p id="accion-texto"></p>
            <small>
              Comparación puntual: el caso no incluye una serie histórica.
              Revisión de gestión propuesta: mensual.
            </small>
          </div>
        </div>
      </article>
    </section>

    <footer>
      <p><strong>AVDM</strong> · Dashboard estratégico</p>
      <p>Fuente: Caso Automotora Viña del Mar S.A.C. y PDO Integral 1.<br>
      Horizonte propuesto: 2027 · Consulta académica</p>
    </footer>

    <noscript>
      <div class="notice">Activa JavaScript para usar los gráficos y filtros.
      La descarga CSV está disponible desde el botón superior.</div>
    </noscript>
  </main>
</div>

<dialog id="detalle" aria-labelledby="detalle-titulo">
  <form method="dialog" class="modal-close">
    <button aria-label="Cerrar detalle">×</button>
  </form>
  <p id="detalle-categoria" class="eyebrow"></p>
  <h2 id="detalle-titulo"></h2>
  <p id="detalle-contexto" class="panel-sub"></p>
  <div class="modal-values">
    <div><small>REFERENCIA DEL CASO</small><strong id="detalle-valor"></strong></div>
    <div><small id="detalle-plazo"></small>
      <strong id="detalle-meta" style="color:var(--verde)"></strong></div>
  </div>
  <p id="detalle-brecha" class="gap"></p>
  <p id="detalle-accion" class="modal-action"></p>
  <p class="modal-note">
    Las referencias no representan resultados observados de 2027.
    Las metas y acciones son propuestas académicas; el stock usa el estándar del caso.
  </p>
</dialog>

<script id="datos" type="application/json">{{ datos | tojson }}</script>
<script>
"use strict";

const datos = JSON.parse(document.getElementById("datos").textContent);
const $ = id => document.getElementById(id);
const numero = new Intl.NumberFormat("es-CL", {maximumFractionDigits: 2});
const estados = {
  umbral: {nombre: "En umbral", color: "#087f72"},
  brecha: {nombre: "Con brecha", color: "#d99b45"},
  pendiente: {nombre: "Sin medición", color: "#a5b5c5"}
};
let categoria = "Todas";

function cantidad(estado) {
  return datos.filter(d => d.estado === estado).length;
}

function diferencia(d) {
  if (d.valor === null) {
    return "Sin medición actual. Primero se necesita establecer una referencia de stock.";
  }
  if (d.estado === "umbral") {
    return "La referencia alcanza el umbral propuesto. El desafío es proteger este nivel.";
  }
  const brecha = Math.abs(d.meta - d.valor);
  if (d.unidad === "h") {
    return `${numero.format(brecha)} h de reducción para alcanzar la meta (−${numero.format(brecha / d.valor * 100)}%).`;
  }
  if (d.unidad === "%") {
    return `${numero.format(brecha)} puntos porcentuales separan la referencia de la meta.`;
  }
  return `US$ ${numero.format(brecha)} M adicionales al mes (+${numero.format(brecha / d.valor * 100)}%).`;
}

function normalizar(texto) {
  return texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

function pintarResumen() {
  $("total").textContent = String(datos.length).padStart(2, "0");
  for (const estado of Object.keys(estados)) {
    $("total-" + estado).textContent = String(cantidad(estado)).padStart(2, "0");
  }
}

function pintarTorta() {
  let avance = 0;
  let segmentos = "";
  let leyenda = "";

  for (const [estado, info] of Object.entries(estados)) {
    const n = cantidad(estado);
    const porcentaje = n / datos.length * 100;

    if (n > 0) {
      segmentos += `
        <circle cx="100" cy="100" r="69" fill="none"
          stroke="${info.color}" stroke-width="27" pathLength="100"
          stroke-dasharray="${porcentaje} ${100 - porcentaje}"
          stroke-dashoffset="${-avance}">
          <title>${info.nombre}: ${n} indicadores, ${numero.format(porcentaje)}%</title>
        </circle>`;
    }
    avance += porcentaje;
    leyenda += `
      <button type="button" data-estado="${estado}">
        <span class="dot" style="background:${info.color}"></span>
        ${info.nombre}
        <strong>${n} · ${numero.format(porcentaje)}%</strong>
      </button>`;
  }

  $("torta").innerHTML = `
    <svg viewBox="0 0 200 200" role="img"
      aria-label="Distribución: ${cantidad("umbral")} en umbral,
      ${cantidad("brecha")} con brecha y ${cantidad("pendiente")} sin medición">
      <g transform="rotate(-90 100 100)">${segmentos}</g>
      <text x="100" y="100" text-anchor="middle"
        fill="#172d3e" font-size="35" font-weight="750">${datos.length}</text>
      <text x="100" y="121" text-anchor="middle"
        fill="#6d8090" font-size="10">INDICADORES</text>
    </svg>`;

  $("leyenda-torta").innerHTML = leyenda;

  document.querySelectorAll("[data-estado]").forEach(boton => {
    boton.addEventListener("click", () => {
      limpiar();
      $("filtro-estado").value = boton.dataset.estado;
      pintarTarjetas();
      $("indicadores").scrollIntoView({block: "start"});
    });
  });
}

function pintarBarras() {
  const items = datos.filter(d => d.unidad === "%" && d.valor !== null);
  const nombres = {
    repuestos: "Repuestos",
    vehiculos: "Vehículos nuevos",
    mercado: "Mercado"
  };
  const maximo = Math.max(10,
    Math.ceil(Math.max(...items.flatMap(d => [d.valor, d.meta])) * 1.15 / 10) * 10);
  const suelo = 218;
  const altura = 175;
  const izquierda = 42;
  const ancho = 505;
  let dibujo = "";

  for (let paso = 0; paso <= 5; paso++) {
    const valor = maximo * paso / 5;
    const y = suelo - altura * paso / 5;
    dibujo += `
      <line x1="${izquierda}" y1="${y}" x2="565" y2="${y}"
        stroke="#e6edf1" stroke-dasharray="3 4"/>
      <text x="33" y="${y + 3}" text-anchor="end"
        fill="#8799a6" font-size="9">${numero.format(valor)}%</text>`;
  }

  items.forEach((d, indice) => {
    const centro = izquierda + ancho / items.length * (indice + 0.5);
    const h1 = altura * d.valor / maximo;
    const h2 = altura * d.meta / maximo;

    dibujo += `
      <rect x="${centro - 35}" y="${suelo - h1}" width="30"
        height="${h1}" rx="4" fill="#087f72">
        <title>${d.nombre}: referencia ${d.texto}</title>
      </rect>
      <rect x="${centro + 5}" y="${suelo - h2}" width="30"
        height="${h2}" rx="4" fill="#a2cfc4">
        <title>${d.nombre}: meta ${d.meta_texto}</title>
      </rect>
      <text x="${centro - 20}" y="${suelo - h1 - 8}"
        text-anchor="middle" fill="#087f72" font-size="10" font-weight="600">
        ${numero.format(d.valor)}%
      </text>
      <text x="${centro + 20}" y="${suelo - h2 - 8}"
        text-anchor="middle" fill="#5f8f82" font-size="10" font-weight="600">
        ${numero.format(d.meta)}%
      </text>
      <text x="${centro}" y="245" text-anchor="middle"
        fill="#6d8090" font-size="10">${nombres[d.id] || d.nombre}</text>`;
  });

  $("barras").innerHTML = `
    <svg class="bar-svg" viewBox="0 0 585 265" role="img"
      aria-label="Barras: repuestos 40% frente a meta 40%;
      vehículos nuevos 12% frente a meta 12%;
      mercado 10,08% frente a meta 11%">
      ${dibujo}
    </svg>`;
}

function pintarTarjetas() {
  const busqueda = normalizar($("buscar").value.trim());
  const estado = $("filtro-estado").value;
  const visibles = datos.filter(d =>
    (categoria === "Todas" || d.categoria === categoria) &&
    (estado === "todos" || d.estado === estado) &&
    normalizar(d.nombre + " " + d.categoria).includes(busqueda)
  );

  $("tarjetas").innerHTML = visibles.map(d => `
    <button type="button" class="card" data-id="${d.id}"
      aria-label="${d.nombre}: ${d.texto}. Ver detalle">
      <span class="category">${d.categoria}</span>
      <span class="card-arrow" aria-hidden="true">↗</span>
      <h3>${d.nombre}</h3>
      <span class="value ${d.valor === null ? "pending" : ""}">${d.texto}</span>
      <span class="context">${d.contexto}</span>
      <span class="card-bottom">
        <span class="target">${d.plazo}<strong>${d.meta_texto}</strong></span>
        <span class="status ${d.estado}">${estados[d.estado].nombre}</span>
      </span>
    </button>`).join("");

  $("resultados").textContent =
    `${visibles.length} ${visibles.length === 1 ? "indicador" : "indicadores"} de ${datos.length}`;
  $("vacio").hidden = visibles.length !== 0;
  $("limpiar").hidden = categoria === "Todas" && estado === "todos" && !busqueda;

  document.querySelectorAll(".card[data-id]").forEach(boton => {
    boton.addEventListener("click", () => abrirDetalle(boton.dataset.id));
  });
}

function actualizarTabs() {
  document.querySelectorAll("[data-categoria]").forEach(boton => {
    const activo = boton.dataset.categoria === categoria;
    boton.classList.toggle("active", activo);
    boton.setAttribute("aria-pressed", String(activo));
  });
}

function limpiar() {
  categoria = "Todas";
  $("buscar").value = "";
  $("filtro-estado").value = "todos";
  actualizarTabs();
  pintarTarjetas();
}

function abrirDetalle(id) {
  const d = datos.find(item => item.id === id);
  $("detalle-categoria").textContent = d.categoria + " · Detalle";
  $("detalle-titulo").textContent = d.nombre;
  $("detalle-contexto").textContent = d.contexto;
  $("detalle-valor").textContent = d.texto;
  $("detalle-meta").textContent = d.meta_texto;
  $("detalle-plazo").textContent = d.plazo.toUpperCase();
  $("detalle-brecha").textContent = diferencia(d);
  $("detalle-accion").textContent = d.accion;
  $("detalle").showModal();
}

document.querySelectorAll("[data-categoria]").forEach(boton => {
  boton.addEventListener("click", () => {
    categoria = boton.dataset.categoria;
    actualizarTabs();
    pintarTarjetas();
  });
});

$("buscar").addEventListener("input", pintarTarjetas);
$("filtro-estado").addEventListener("change", pintarTarjetas);
$("limpiar").addEventListener("click", limpiar);

$("restablecer")?.addEventListener("click", limpiar);
$("imprimir")?.addEventListener("click", () => window.print());

$("detalle").querySelector("button")?.addEventListener("click", () => {
  $("detalle").close();
});

function pintarComparativo() {
  const selector = $("comparar");
  const grafico = $("grafico");
  if (!selector || !grafico) return;

  const d = datos.find(item => item.id === selector.value);
  if (!d) return;

  if (d.valor === null) {
    grafico.textContent = "Sin medición actual. Estándar del caso: > 95%.";
    return;
  }

  const maximo = Math.max(d.valor, d.meta) * 1.12;
  grafico.innerHTML = `
    <p>Referencia del caso: <strong>${d.texto}</strong></p>
    <div style="height:16px;background:#edf3f5;border-radius:5px;margin:10px 0 20px">
      <div style="height:100%;width:${d.valor / maximo * 100}%;background:#087f72;border-radius:5px"></div>
    </div>
    <p>${d.plazo}: <strong>${d.meta_texto}</strong></p>
    <div style="height:16px;background:#edf3f5;border-radius:5px;margin:10px 0 20px">
      <div style="height:100%;width:${d.meta / maximo * 100}%;background:#a2cfc4;border-radius:5px"></div>
    </div>
    <p>${diferencia(d)}</p>`;
}

$("comparar")?.addEventListener("change", pintarComparativo);

pintarResumen();
pintarTorta();
pintarBarras();
actualizarTabs();
pintarTarjetas();
pintarComparativo();
</script>
</body>
</html>
"""


@app.get("/")
def inicio():
    return render_template_string(PAGINA, datos=DATOS)


@app.get("/descargar.csv")
def descargar():
    archivo = io.StringIO()
    escritor = csv.writer(archivo, delimiter=";")
    escritor.writerow([
        "Indicador", "Categoria", "Referencia",
        "Unidad", "Meta", "Plazo", "Estado"
    ])

    for d in DATOS:
        escritor.writerow([
            d["nombre"],
            d["categoria"],
            "Sin medicion" if d["valor"] is None else d["valor"],
            d["unidad"],
            d["meta_texto"],
            d["plazo"],
            d["estado"],
        ])

    return Response(
        "\ufeff" + archivo.getvalue(),
        content_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition":
            'attachment; filename="indicadores-automotora.csv"'
        },
    )


if __name__ == "__main__":
    app.run()
