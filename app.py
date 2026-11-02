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
/* Ajustes de legibilidad, controles y acceso con teclado. */
:root{--fluida:cubic-bezier(.22,1,.36,1)}
.slice{transition:stroke-width .45s var(--fluida),opacity .45s ease,filter .3s ease}
.donut-svg .slice{transition:stroke-dasharray 1s var(--fluida),stroke-dashoffset 1s var(--fluida),stroke .7s ease,stroke-width .45s var(--fluida),opacity .45s ease}
.donut-svg .slice:hover{stroke-width:34px!important;filter:drop-shadow(0 2px 2px #173b3915)}
.pie-number{fill:white;font-size:11px;font-weight:750;pointer-events:none;paint-order:stroke;stroke:#244b4525;stroke-width:1px;transition:transform 1s var(--fluida),opacity .45s ease}
.pie-center{font-size:26px;font-weight:750;fill:#172d3e;letter-spacing:-1px}
.pie-subtitle{font-size:7px;letter-spacing:.6px;fill:#6d8090}
.pie-goal{font-size:8px;fill:#6d8090}
.torta-controls{display:grid;gap:7px;margin-top:17px}
.torta-controls label{font-size:11px;color:var(--muted)}
.torta-controls select{width:100%;min-height:40px;background:#f8fbfa}
.torta-actions{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin-top:15px}
.torta-actions .button{font-size:10px;padding:9px 11px}
.torta-sin-dato{font-size:12px;line-height:1.8;color:var(--muted)}
.legend strong{display:block;font-size:11px;line-height:1.5}
.legend strong small{display:block;font-size:9px;color:var(--muted);font-weight:400}
.legend button{justify-content:flex-start;min-width:0}
.legend button>span:nth-child(2){flex:1;min-width:0}
.donut-wrap .donut{width:205px;flex-shrink:0}
@media print{.torta-controls,.torta-actions{display:none!important}.donut-svg .slice,.pie-number{transition:none!important}}
.data-bar{transition:x .75s var(--fluida),y .75s var(--fluida),height .75s var(--fluida),width .75s var(--fluida),opacity .4s ease}
.bar-number{transition:transform .75s var(--fluida),opacity .4s ease}
.fill{transition:width .85s var(--fluida)}
.comparison-bars{max-height:340px;opacity:1;overflow:hidden;transition:max-height .6s var(--fluida),opacity .35s ease,transform .5s var(--fluida);transform:translateY(0)}
#comparacion .missing-comparison{max-height:0;opacity:0;padding:0;overflow:hidden;transform:translateY(10px);transition:max-height .6s var(--fluida),opacity .4s ease,transform .5s var(--fluida),padding .5s ease}
#comparacion.is-missing .comparison-bars{max-height:0;opacity:0;transform:translateY(-6px)}
#comparacion.is-missing .missing-comparison{max-height:280px;opacity:1;padding:10px 0 20px;transform:translateY(0)}
dialog[open]{animation:aparecer-modal .25s var(--fluida)}
dialog[open]::backdrop{animation:aparecer-fondo .25s ease}
@keyframes aparecer-modal{from{opacity:0;transform:translateY(14px) scale(.98)}to{opacity:1;transform:translateY(0) scale(1)}}
@keyframes aparecer-fondo{from{background:transparent}to{background:#15374877}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
@media print{*,*::before,*::after{animation:none!important;transition:none!important}.is-missing .comparison-bars{display:none}.comparison-bars[aria-hidden="false"]{max-height:none!important}.missing-comparison[aria-hidden="true"]{display:none!important}}
.summary-card{text-align:left;color:var(--texto);font:inherit;cursor:pointer;transition:border-color .18s,transform .18s}
.summary-card:hover{border-color:#76b6a9;transform:translateY(-2px)}
.summary-card[aria-pressed="true"]{box-shadow:inset 0 0 0 1px #087f72;border-color:#087f72}
.summary-card span{display:block;line-height:1.6}
.panel-controls{display:flex;justify-content:space-between;gap:12px;align-items:center;margin-top:16px;flex-wrap:wrap}
.panel-controls label{font-size:11px;color:var(--muted)}
.panel-controls select{padding:8px;font-size:11px}
.slice,.bar-group{cursor:pointer}
.slice:hover{stroke-width:32}
.slice:focus-visible{outline:none;stroke-width:34;filter:drop-shadow(0 0 2px #174639)}
.bar-group:hover .data-bar,.bar-group:focus-visible .data-bar{stroke:#164d45;stroke-width:2}
.bar-group:focus-visible{outline:2px solid #087f72;outline-offset:2px}
.legend button[aria-pressed="true"]{box-shadow:inset 0 0 0 1px #087f72;background:#e8f6f1}
.legend button{min-height:40px;line-height:1.5;flex-wrap:wrap}
.legend strong{white-space:nowrap}
.chart-grid>.panel{overflow:visible}
.missing-comparison{padding:10px 0 20px;line-height:1.8}
.missing-comparison h3{margin:18px 0 10px}
.missing-comparison p{font-size:12px;color:#58717f;margin:8px 0}
.action-panel .button{margin-top:15px;font-size:11px}
.empty .button{margin-top:18px}
.modal-buttons{margin-top:20px}
.modal-note{line-height:1.7}
nav a:first-child{background:transparent;color:var(--muted)}
nav a[aria-current="location"],nav a:hover{color:var(--verde);background:var(--verde-claro)}
.skip-link{position:absolute;top:8px;left:8px;z-index:99;background:#fff;padding:12px;border:1px solid #087f72;transform:translateY(-160%)}
.skip-link:focus{transform:none}
.section-head h2:focus{outline:none}
.card h3{font-size:14px}.context{font-size:11px}.category{font-size:10px}
.summary-card p,.panel-sub{font-size:12px}.summary-card span{font-size:10px}
.panel h3{font-size:18px}.legend button,.chart-legend{font-size:11px}
.donut-note{font-size:11px;line-height:1.75}.bar-label{font-size:12px}
.target{font-size:10px}.status{font-size:10px}.result-line{font-size:12px}
.inputs input,.inputs select{font-size:12px;min-height:42px}
.tab{font-size:12px;min-height:42px}.subtitle{font-size:14px}.notice{font-size:12px}
.chart-legend{flex-wrap:wrap}.bar-svg{min-width:0}
.donut-wrap{gap:16px}.donut{width:185px;max-width:46%}.legend{min-width:0}
.comparison-select{margin-top:8px;font-size:13px;min-height:44px}
.bar-row{margin-bottom:25px}.gap{font-size:12px}
footer{font-size:10px}
@media(max-width:1150px){.donut-wrap{flex-direction:column}.donut{max-width:100%;width:175px}.chart-grid{grid-template-columns:1fr 1.3fr}}
@media(max-width:850px){.chart-grid{grid-template-columns:1fr}.donut-wrap{flex-direction:row;justify-content:space-around}.donut{max-width:45%;width:190px}.legend{width:auto}.sidebar{display:none}}
@media(max-width:580px){.hero h1{font-size:29px}.summary-card span{font-size:9px;letter-spacing:.4px}.summary-card p{font-size:11px}.summary-card{padding:14px}.card h3{font-size:13px;min-height:50px}.card{min-height:280px}.context{font-size:11px}.value{font-size:27px}.notice{font-size:11px}.panel-sub,.donut-note{font-size:11px}.section-head p{font-size:10px}.donut-wrap{gap:8px}.donut{width:155px;max-width:44%}.legend button{font-size:10px;padding:9px 7px;gap:5px}.legend strong{margin-left:0}.panel{padding:16px}.inputs{flex-wrap:wrap}.inputs input{width:100%}.inputs select{width:100%}.tabs{overflow-x:auto;justify-content:space-between}.tab{padding:8px 10px;font-size:11px}.card-bottom{display:block}.status{display:inline-block;margin-top:9px}.modal-values strong{font-size:22px}.action-panel p{font-size:12px}.comparison-layout{gap:15px}.card-arrow{top:9px}footer{font-size:9px}.button{min-height:42px}}
@media(max-width:380px){.cards{grid-template-columns:1fr}.card{min-height:220px}.card h3{min-height:0}.donut-wrap{flex-direction:column}.donut{max-width:100%;width:170px}.legend{width:100%}.legend button{justify-content:space-between}.chart-legend{font-size:10px}.summary-card strong{font-size:28px}}
@media print{.panel-controls,.modal-buttons,.skip-link,.action-panel .button{display:none!important}.summary-card{box-shadow:none!important;transform:none}.card:hover{transform:none}.donut-wrap{flex-direction:column}.card h3{font-size:11px}.context,.donut-note{font-size:9px}.summary-card p{font-size:8px}.summary-card span{font-size:7px}.card{min-height:230px}.chart-grid{grid-template-columns:1fr 1.3fr}.summary{grid-template-columns:repeat(4,1fr)}footer{font-size:8px}}

</style>
</head>
<body>
<a class="skip-link" href="#contenido">Ir al contenido</a>
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

  <main id="contenido">
    <section class="hero" id="inicio">
      <div>
        <p class="eyebrow">AUTOMOTORA VIÑA DEL MAR S.A.C.</p>
        <h1>El negocio, en perspectiva<span>.</span></h1>
        <p class="subtitle">Crecimiento rentable, servicio ágil y disponibilidad.</p>
      </div>
      <div class="actions">
        <button class="button" id="imprimir" type="button">↗ Imprimir vista</button>
        <a class="button primary" href="{{ url_for('descargar') }}">↓ Descargar CSV</a>
      </div>
    </section>

    <div class="notice">
      <strong>Contexto de lectura.</strong>
      Las cifras son referencias del caso. Las metas 2027 son propuestas académicas;
      el estándar de stock proviene del caso. No hay actualización automática de datos.
    </div>

    <section class="summary" aria-label="Resumen de indicadores">
      <button class="summary-card" type="button" data-resumen="todos" aria-pressed="false">
        <span>INDICADORES ESTRATÉGICOS</span>
        <strong id="total">{{ datos | length }}</strong>
        <p>3 financieros · 3 no financieros</p>
      </button>
      <button class="summary-card" type="button" data-resumen="umbral" aria-pressed="false">
        <span>REFERENCIAS EN UMBRAL</span>
        <strong id="total-umbral" style="color:var(--verde)"></strong>
        <p>Referencias que alcanzan el umbral</p>
      </button>
      <button class="summary-card" type="button" data-resumen="brecha" aria-pressed="false">
        <span>BRECHAS FRENTE A META</span>
        <strong id="total-brecha" style="color:var(--ambar)"></strong>
        <p>Oportunidades de mejora</p>
      </button>
      <button class="summary-card" type="button" data-resumen="pendiente" aria-pressed="false">
        <span>MEDICIÓN PENDIENTE</span>
        <strong id="total-pendiente">{{ datos | selectattr("estado", "equalto", "pendiente") | list | length }}</strong>
        <p>Indicadores sin referencia medida</p>
      </button>
    </section>

    <section id="graficos">
      <div class="section-head">
        <div>
          <p class="eyebrow">PANORAMA VISUAL</p>
          <h2>Tres formas de entender el desempeño</h2>
        </div>
        <p>Gráficos del caso completo · los estados filtran las tarjetas</p>
      </div>
      <div class="chart-grid">
        <article class="panel">
          <h3>Comparación circular</h3>
          <p class="panel-sub">Explora las cifras del caso y su distancia a las metas.</p>
<div class="torta-controls"><label for="vista-torta">¿Qué quieres comparar?</label><select id="vista-torta"><optgroup label="Vista general"><option value="estados">Estados frente a metas</option><option value="perspectivas">Perspectivas del CMI</option></optgroup><optgroup label="Referencia y brecha hasta la meta">{% for item in datos %}<option value="{{ item.id }}">{{ item.nombre }}</option>{% endfor %}</optgroup></select></div>
          <div class="donut-wrap">
            <div id="torta" class="donut"></div>
            <div id="leyenda-torta" class="legend"></div>
          </div>
          <p id="torta-explicacion" class="donut-note"></p><div class="torta-actions"><button id="torta-accion" type="button" class="button">Ver indicadores ↗</button><button id="reiniciar-torta" type="button" class="text-button">Restablecer círculo</button></div>
        </article>

        <article class="panel">
          <h3>Márgenes y participación</h3>
          <p class="panel-sub">
            Referencias y metas de los tres indicadores con medición expresada en porcentaje.
          </p>
          <div class="panel-controls"><label for="series-barras">Series del gráfico</label><select id="series-barras"><option value="ambas">Referencia y meta</option><option value="referencia">Solo referencia</option><option value="meta">Solo meta</option></select></div><div id="barras"></div>
          <div class="chart-legend">
            <span id="leyenda-referencia"><i style="background:#087f72"></i>Referencia del caso</span>
            <span id="leyenda-meta"><i style="background:#a2cfc4"></i>Meta propuesta</span>
          </div>
          <p class="donut-note">
            Selecciona un grupo de barras para ver su detalle. Cada indicador se compara con su propia meta.
          </p>
        </article>
      </div>
    </section>

    <section id="indicadores">
      <div class="section-head">
        <div>
          <p class="eyebrow">CUADRO DE MANDO</p>
          <h2 id="indicadores-titulo" tabindex="-1">Los indicadores que importan</h2>
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
      <div id="vacio" class="empty" hidden><p>No encontramos indicadores. Prueba otra búsqueda o limpia los filtros.</p><button id="restablecer" class="button" type="button">Mostrar todos</button></div>
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
            <p id="accion-texto"></p><button id="abrir-comparado" class="button" type="button">Ver detalle del indicador ↗</button>
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
  <p id="detalle-accion" class="modal-action"></p><div class="modal-buttons"><button id="ver-comparacion" class="button primary" type="button">Comparar este indicador ↗</button></div>
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
  brecha: {nombre: "Con brecha", color: "#c88832"},
  pendiente: {nombre: "Sin medición", color: "#8c9fae"}
};
let categoria = "Todas";
let detalleActual = datos[0].id;
const normalizar = texto => texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
const escapar = texto => String(texto).replace(/[&<>"']/g, letra => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[letra]));
const cantidad = estado => datos.filter(d => d.estado === estado).length;
const movimientoReducido = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
function textoSuave(elemento, texto) {
  if (elemento.textContent === texto) return;
  elemento.textContent = texto;
  if (!movimientoReducido()) elemento.animate([{opacity: 0.35, transform: "translateY(3px)"}, {opacity: 1, transform: "translateY(0)"}], {duration: 220, easing: "ease-out"});
}

function diferencia(d) {
  if (d.valor === null) return "Sin medición actual. Primero se necesita establecer una referencia de stock.";
  if (d.estado === "umbral") return "La referencia alcanza el umbral propuesto. El desafío es proteger este nivel.";
  const brecha = Math.abs(d.meta - d.valor);
  if (d.unidad === "h") return `${numero.format(brecha)} h de reducción para alcanzar la meta (−${numero.format(brecha / d.valor * 100)}%).`;
  if (d.unidad === "%") return `${numero.format(brecha)} puntos porcentuales separan la referencia de la meta.`;
  return `US$ ${numero.format(brecha)} M adicionales al mes (+${numero.format(brecha / d.valor * 100)}%).`;
}

function actualizarTabs() {
  document.querySelectorAll("[data-categoria]").forEach(boton => {
    const activo = boton.dataset.categoria === categoria;
    boton.classList.toggle("active", activo);
    boton.setAttribute("aria-pressed", String(activo));
  });
  document.querySelectorAll(".summary-card").forEach(boton => {
    const activo = boton.dataset.resumen === $("filtro-estado").value && categoria === "Todas" && !$("buscar").value.trim();
    boton.setAttribute("aria-pressed", String(activo));
  });
}

function pintarTarjetas() {
  const posiciones = new Map([...$("tarjetas").querySelectorAll(".card")].map(elemento => [elemento.dataset.id, elemento.getBoundingClientRect()]));
  const busqueda = normalizar($("buscar").value.trim());
  const estado = $("filtro-estado").value;
  const visibles = datos.filter(d => (categoria === "Todas" || d.categoria === categoria) && (estado === "todos" || d.estado === estado) && normalizar(d.nombre + " " + d.categoria).includes(busqueda));
  $("tarjetas").replaceChildren(...visibles.map(d => {
    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "card";
    boton.dataset.id = d.id;
    boton.setAttribute("aria-label", `${d.nombre}: ${d.texto}. Ver detalle`);
    boton.innerHTML = `<span class="category">${escapar(d.categoria)}</span><span class="card-arrow" aria-hidden="true">↗</span><h3>${escapar(d.nombre)}</h3><span class="value ${d.valor === null ? "pending" : ""}">${escapar(d.texto)}</span><span class="context">${escapar(d.contexto)}</span><span class="card-bottom"><span class="target">${escapar(d.plazo)}<strong>${escapar(d.meta_texto)}</strong></span><span class="status ${d.estado}">${estados[d.estado].nombre}</span></span>`;
    boton.addEventListener("click", () => abrirDetalle(d.id));
    return boton;
  }));
  $("resultados").textContent = `${visibles.length} ${visibles.length === 1 ? "indicador" : "indicadores"} de ${datos.length}`;
  $("vacio").hidden = visibles.length !== 0;
  $("limpiar").hidden = categoria === "Todas" && estado === "todos" && !busqueda;
  if (!movimientoReducido()) $("tarjetas").querySelectorAll(".card").forEach((elemento, indice) => {
    const antes = posiciones.get(elemento.dataset.id);
    const ahora = elemento.getBoundingClientRect();
    elemento.animate([{opacity: antes ? 1 : 0, transform: antes ? `translate(${antes.left - ahora.left}px, ${antes.top - ahora.top}px)` : "translateY(12px)"}, {opacity: 1, transform: "translate(0, 0)"}], {duration: 320, delay: antes ? 0 : indice * 30, easing: "cubic-bezier(.22,1,.36,1)"});
  });
  actualizarTabs();
}

function limpiar() {
  categoria = "Todas";
  $("buscar").value = "";
  $("filtro-estado").value = "todos";
  pintarTarjetas();
  pintarTorta();
}

function filtrarEstado(estado) {
  categoria = "Todas";
  $("buscar").value = "";
  $("filtro-estado").value = estado;
  pintarTarjetas();
  pintarTorta();
  $("indicadores").scrollIntoView({block: "start", behavior: "smooth"});
  $("indicadores-titulo").focus({preventScroll: true});
}

function pintarResumen() {
  $("total").textContent = String(datos.length).padStart(2, "0");
  Object.keys(estados).forEach(estado => $("total-" + estado).textContent = String(cantidad(estado)).padStart(2, "0"));
}

let seleccionTorta = null;
let modoTortaAnterior = "";
const cuentasTorta = new WeakMap();

function contarSuave(elemento, valor, formato) {
  if (cuentasTorta.has(elemento)) cancelAnimationFrame(cuentasTorta.get(elemento));
  const desde = Number(elemento.dataset.numero || 0);
  if (movimientoReducido() || desde === valor) {
    elemento.textContent = formato(valor);
    elemento.dataset.numero = valor;
    return;
  }
  const inicio = performance.now();
  const paso = tiempo => {
    const progreso = Math.min(1, (tiempo - inicio) / 650);
    const actual = desde + (valor - desde) * (1 - Math.pow(1 - progreso, 3));
    elemento.dataset.numero = actual;
    elemento.textContent = formato(actual);
    if (progreso < 1) cuentasTorta.set(elemento, requestAnimationFrame(paso));
    else {elemento.dataset.numero = valor; elemento.textContent = formato(valor); cuentasTorta.delete(elemento);}
  };
  cuentasTorta.set(elemento, requestAnimationFrame(paso));
}

function modeloTorta() {
  const modo = $("vista-torta").value;
  const entero = valor => String(Math.round(valor));
  if (modo === "estados") return {
    modo, total: datos.length, valor: datos.length, formato: entero, subtitulo: "INDICADORES", objetivo: "Vista completa del caso",
    descripcion: "El círculo cuenta indicadores. Selecciona un sector o su leyenda para explorar un estado.",
    grupos: Object.entries(estados).map(([clave, info]) => ({clave, nombre: info.nombre, n: cantidad(clave), color: info.color, formato: entero})),
    activo: $("filtro-estado").value === "todos" ? null : $("filtro-estado").value
  };
  if (modo === "perspectivas") return {
    modo, total: datos.length, valor: datos.length, formato: entero, subtitulo: "INDICADORES", objetivo: "Perspectivas del CMI",
    descripcion: "Cantidad de indicadores por perspectiva. Cada sector permite explorar sus tarjetas.",
    grupos: ["Finanzas", "Clientes", "Procesos"].map((nombre, i) => ({clave: nombre, nombre, n: datos.filter(d => d.categoria === nombre).length, color: ["#087f72", "#4e91ab", "#c88832"][i], formato: entero})),
    activo: categoria === "Todas" ? null : categoria
  };
  const d = datos.find(item => item.id === modo);
  const formato = valor => d.unidad === "M USD" ? `${numero.format(valor)} M` : `${numero.format(valor)}${d.unidad === "%" ? "%" : " h"}`;
  const formatoLeyenda = valor => d.unidad === "M USD" ? `US$ ${numero.format(valor)} M` : formato(valor);
  const base = {modo, indicador: d, valor: d.valor, formato, subtitulo: "REFERENCIA DEL CASO", objetivo: `Meta: ${d.meta_texto}`, activo: seleccionTorta};
  if (d.valor === null) return {...base, total: 0, grupos: [], descripcion: "Sin medición de referencia: no es posible calcular una proporción. El estándar del caso es > 95%."};
  let grupos;
  if (d.operador === "≤" && d.valor > d.meta) {
    grupos = [{clave: "objetivo", nombre: "Plazo objetivo", n: d.meta, color: "#087f72"}, {clave: "brecha", nombre: "Reducción necesaria", n: d.valor - d.meta, color: "#c88832"}];
    base.total = d.valor;
    base.descripcion = `El círculo representa ${formato(d.valor)} de referencia: distingue el plazo objetivo de las horas que se propone reducir.`;
  } else if (d.operador === "≤") {
    grupos = [{clave: "referencia", nombre: "Plazo de referencia", n: d.valor, color: "#087f72"}, {clave: "holgura", nombre: "Holgura hasta el límite", n: d.meta - d.valor, color: "#8fbfb3"}];
    base.total = d.meta;
    base.descripcion = "Referencia de tiempo y holgura hasta el plazo máximo propuesto.";
  } else if (d.valor <= d.meta) {
    grupos = [{clave: "referencia", nombre: "Referencia del caso", n: d.valor, color: "#087f72"}, {clave: "brecha", nombre: "Brecha hasta la meta", n: d.meta - d.valor, color: "#c88832"}];
    base.total = d.meta;
    base.descripcion = "El círculo completo representa la meta. El sector ámbar muestra cuánto falta desde la referencia del caso.";
  } else {
    grupos = [{clave: "meta", nombre: "Meta cubierta", n: d.meta, color: "#087f72"}, {clave: "excedente", nombre: "Sobre la meta", n: d.valor - d.meta, color: "#8fbfb3"}];
    base.total = d.valor;
    base.descripcion = "El círculo representa la referencia: distingue la meta cubierta del valor que la supera.";
  }
  return {...base, grupos: grupos.map(grupo => ({...grupo, formato: grupo.clave === "brecha" && d.unidad === "%" ? valor => `${numero.format(valor)} pp` : formatoLeyenda}))};
}

function elegirSectorTorta(clave) {
  const modelo = modeloTorta();
  seleccionTorta = clave;
  if (modelo.modo === "estados") {
    categoria = "Todas";
    $("buscar").value = "";
    $("filtro-estado").value = clave;
    pintarTarjetas();
  } else if (modelo.modo === "perspectivas") {
    categoria = clave;
    $("buscar").value = "";
    $("filtro-estado").value = "todos";
    pintarTarjetas();
  }
  pintarTorta();
}

function pintarTorta() {
  const modelo = modeloTorta();
  const nuevo = !$("torta").querySelector("svg");
  if (modelo.modo !== modoTortaAnterior) {seleccionTorta = null; modelo.activo = null; modoTortaAnterior = modelo.modo;}
  if (nuevo) {
    $("torta").innerHTML = `<svg class="donut-svg" viewBox="0 0 220 220" aria-label="Comparación circular"><circle cx="110" cy="110" r="76" fill="none" stroke="#edf2f5" stroke-width="28"/><g transform="rotate(-90 110 110)">${[0,1,2].map(i => `<circle class="slice" data-sector-indice="${i}" role="button" tabindex="0" cx="110" cy="110" r="76" fill="none" stroke-width="28" pathLength="100" stroke-dasharray="0 100"/>`).join("")}</g>${[0,1,2].map(i => `<text class="pie-number" data-cifra-sector="${i}" text-anchor="middle" dominant-baseline="middle"></text>`).join("")}<text class="pie-center" x="110" y="103" text-anchor="middle">6</text><text class="pie-subtitle" x="110" y="122" text-anchor="middle">INDICADORES</text><text class="pie-goal" x="110" y="139" text-anchor="middle"></text></svg>`;
    document.querySelectorAll("[data-sector-indice]").forEach(sector => {
      const activar = () => {if (sector.dataset.sector) elegirSectorTorta(sector.dataset.sector);};
      sector.addEventListener("click", activar);
      sector.addEventListener("keydown", evento => {if (["Enter", " "].includes(evento.key)) {evento.preventDefault(); activar();}});
    });
  }
  const svg = $("torta").querySelector("svg");
  svg.setAttribute("aria-label", modelo.indicador ? `${modelo.indicador.nombre}. Referencia ${modelo.indicador.texto}; meta ${modelo.indicador.meta_texto}` : `${modelo.total} indicadores: ${modelo.grupos.map(g => `${g.nombre} ${g.n}`).join(", ")}`);
  const dibujar = () => {
    let avance = 0;
    document.querySelectorAll("[data-sector-indice]").forEach((sector, indice) => {
      const grupo = modelo.grupos[indice];
      const porcentaje = grupo && modelo.total ? grupo.n / modelo.total * 100 : 0;
      const activo = grupo && modelo.activo === grupo.clave;
      sector.dataset.sector = grupo ? grupo.clave : "";
      sector.style.stroke = grupo ? grupo.color : "transparent";
      sector.style.strokeDasharray = `${porcentaje} ${100 - porcentaje}`;
      sector.style.strokeDashoffset = String(-avance);
      sector.style.strokeWidth = activo ? "34px" : "28px";
      sector.style.opacity = grupo && porcentaje ? (modelo.activo && !activo ? ".5" : "1") : "0";
      sector.setAttribute("tabindex", grupo && porcentaje ? "0" : "-1");
      sector.setAttribute("aria-hidden", String(!grupo || !porcentaje));
      sector.setAttribute("aria-pressed", String(Boolean(activo)));
      sector.setAttribute("aria-label", grupo ? `${grupo.nombre}: ${grupo.formato(grupo.n)}, ${numero.format(porcentaje)}%. Seleccionar sector` : "");
      const cifra = svg.querySelector(`[data-cifra-sector="${indice}"]`);
      const angulo = (avance + porcentaje / 2) / 100 * 2 * Math.PI - Math.PI / 2;
      cifra.style.transform = `translate(${110 + 76 * Math.cos(angulo)}px, ${110 + 76 * Math.sin(angulo)}px)`;
      cifra.style.opacity = grupo && porcentaje >= 4 ? "1" : "0";
      cifra.textContent = grupo ? numero.format(grupo.n) : "";
      avance += porcentaje;
    });
  };
  if (nuevo && !movimientoReducido()) {svg.getBoundingClientRect(); requestAnimationFrame(dibujar);} else dibujar();
  const activo = modelo.grupos.find(g => g.clave === modelo.activo);
  const centro = svg.querySelector(".pie-center");
  if (modelo.valor === null) {
    if (cuentasTorta.has(centro)) cancelAnimationFrame(cuentasTorta.get(centro));
    centro.textContent = "—";
    centro.dataset.numero = "0";
  } else contarSuave(centro, activo ? activo.n : modelo.valor, activo ? activo.formato : modelo.formato);
  svg.querySelector(".pie-subtitle").textContent = modelo.valor === null ? "POR MEDIR" : (activo ? activo.nombre : modelo.subtitulo).toUpperCase();
  svg.querySelector(".pie-goal").textContent = activo ? `${numero.format(activo.n / modelo.total * 100)}% DEL CÍRCULO` : modelo.objetivo;
  $("leyenda-torta").innerHTML = modelo.grupos.length ? modelo.grupos.map(grupo => `<button type="button" data-estado="${escapar(grupo.clave)}" aria-pressed="${modelo.activo === grupo.clave}"><span class="dot" style="background:${grupo.color}"></span><span>${escapar(grupo.nombre)}</span><strong>${escapar(grupo.formato(grupo.n))}<small>${numero.format(grupo.n / modelo.total * 100)}% del círculo</small></strong></button>`).join("") : '<p class="torta-sin-dato">No hay una referencia medida para comparar con el estándar.</p>';
  document.querySelectorAll("#leyenda-torta [data-estado]").forEach(boton => boton.addEventListener("click", () => {elegirSectorTorta(boton.dataset.estado); $("leyenda-torta").querySelector(`[data-estado="${boton.dataset.estado}"]`)?.focus({preventScroll:true});}));
  $("torta-explicacion").textContent = modelo.descripcion;
  $("torta-accion").textContent = modelo.indicador ? "Comparar este indicador ↗" : "Ver indicadores ↗";
}


function pintarBarras() {
  const items = datos.filter(d => d.unidad === "%" && d.valor !== null);
  const modo = $("series-barras").value;
  const nombres = {repuestos: "Repuestos", vehiculos: "Vehículos nuevos", mercado: "Mercado"};
  const maximo = Math.max(10, Math.ceil(Math.max(...items.flatMap(d => [d.valor, d.meta])) * 1.15 / 10) * 10);
  const suelo = 218, altura = 175, izquierda = 42, ancho = 505;
  let dibujo = "";
  for (let paso = 0; paso <= 5; paso++) {
    const y = suelo - altura * paso / 5;
    dibujo += `<line x1="42" y1="${y}" x2="565" y2="${y}" stroke="#e6edf1" stroke-dasharray="3 4"/><text x="33" y="${y + 3}" text-anchor="end" fill="#748898" font-size="10">${numero.format(maximo * paso / 5)}%</text>`;
  }
  items.forEach((d, indice) => {
    const centro = izquierda + ancho / items.length * (indice + 0.5);
    dibujo += `<g class="bar-group" role="button" tabindex="0" data-barra="${d.id}" data-centro="${centro}" aria-label="Ver ${escapar(d.nombre)}: referencia ${d.texto}, meta ${d.meta_texto}"><title>${escapar(d.nombre)} · Referencia ${d.texto} · Meta ${d.meta_texto}</title><rect x="${centro - 68}" y="28" width="136" height="225" fill="transparent"/>`;
    for (const serie of ["referencia", "meta"]) {
      const valor = serie === "referencia" ? d.valor : d.meta;
      const h = altura * valor / maximo;
      const x = centro + (modo === "ambas" ? (serie === "referencia" ? -35 : 5) : -15);
      dibujo += `<rect class="data-bar" data-serie="${serie}" data-altura="${h}" x="${x}" y="${suelo}" width="30" height="0" rx="4" fill="${serie === "referencia" ? "#087f72" : "#a2cfc4"}"/><text class="bar-number" data-numero="${serie}" x="${x + 15}" y="${suelo - h - 9}" opacity="0" text-anchor="middle" fill="#385a67" font-size="11" font-weight="600">${numero.format(valor)}%</text>`;
    }
    dibujo += `<text x="${centro}" y="245" text-anchor="middle" fill="#5e7586" font-size="11">${nombres[d.id] || escapar(d.nombre)}</text></g>`;
  });
  const nuevo = !$("barras").querySelector("svg");
  if (nuevo) $("barras").innerHTML = `<svg class="bar-svg" viewBox="0 0 585 265" aria-label="Referencias y metas en porcentaje; selecciona un indicador para ver el detalle">${dibujo}</svg>`;
  $("leyenda-referencia").hidden = modo === "meta";
  $("leyenda-meta").hidden = modo === "referencia";
  const ajustar = () => document.querySelectorAll("[data-barra]").forEach(grupo => {
    const centro = Number(grupo.dataset.centro);
    grupo.querySelectorAll("[data-serie]").forEach(barra => {
      const serie = barra.dataset.serie;
      const visible = modo === "ambas" || modo === serie;
      const h = visible ? Number(barra.dataset.altura) : 0;
      const x = centro + (modo === "ambas" ? (serie === "referencia" ? -35 : 5) : -15);
      barra.dataset.visible = String(visible);
      barra.setAttribute("aria-hidden", String(!visible));
      barra.style.x = `${x}px`;
      barra.style.y = `${suelo - h}px`;
      barra.style.height = `${h}px`;
      barra.style.width = visible ? "30px" : "0px";
      barra.style.opacity = visible ? "1" : "0";
      const etiqueta = grupo.querySelector(`[data-numero="${serie}"]`);
      etiqueta.setAttribute("aria-hidden", String(!visible));
      etiqueta.style.transform = `translateX(${x + 15 - Number(etiqueta.getAttribute("x"))}px)`;
      etiqueta.style.opacity = visible ? "1" : "0";
    });
  });
  if (nuevo) {
    document.querySelectorAll("[data-barra]").forEach(grupo => {
      grupo.addEventListener("click", () => abrirDetalle(grupo.dataset.barra));
      grupo.addEventListener("keydown", evento => {if (["Enter", " "].includes(evento.key)) {evento.preventDefault(); abrirDetalle(grupo.dataset.barra);}});
    });
    $("barras").getBoundingClientRect();
    if (movimientoReducido()) ajustar(); else requestAnimationFrame(ajustar);
  } else ajustar();
}

function pintarComparativo() {
  const d = datos.find(item => item.id === $("comparar").value) || datos[0];
  textoSuave($("accion-titulo"), d.nombre);
  textoSuave($("accion-texto"), d.accion);
  $("abrir-comparado").dataset.id = d.id;
  const nuevo = !$("comparacion").querySelector(".comparison-bars");
  if (nuevo) {
    $("comparacion").innerHTML = `<div class="comparison-bars"><div class="bar-row"><div class="bar-label"><span>Referencia del caso</span><strong data-comparacion="valor"></strong></div><div class="track"><div class="fill" data-fill="valor" style="width:0%"></div></div></div><div class="bar-row"><div class="bar-label"><span data-comparacion="plazo"></span><strong data-comparacion="meta"></strong></div><div class="track"><div class="fill goal" data-fill="meta" style="width:0%"></div></div></div><p class="gap" data-comparacion="brecha"></p></div><div class="missing-comparison" aria-hidden="true"><span class="status pendiente">Sin medición</span><h3>Una referencia por construir</h3><p>Estándar del caso: <strong data-comparacion="estandar"></strong>.</p><p>No se dibuja una barra de resultado porque el caso no informa un valor actual.</p></div>`;
  }
  const contenedor = $("comparacion");
  const pendiente = d.valor === null;
  contenedor.classList.toggle("is-missing", pendiente);
  contenedor.querySelector(".comparison-bars").setAttribute("aria-hidden", String(pendiente));
  contenedor.querySelector(".missing-comparison").setAttribute("aria-hidden", String(!pendiente));
  for (const [campo, texto] of Object.entries({valor: d.texto, plazo: d.plazo, meta: d.meta_texto, brecha: diferencia(d), estandar: d.meta_texto})) textoSuave(contenedor.querySelector(`[data-comparacion="${campo}"]`), texto);
  const maximo = Math.max(d.valor || 0, d.meta) * 1.12;
  const ajustar = () => {
    contenedor.querySelector('[data-fill="valor"]').style.width = pendiente ? "0%" : `${100 * d.valor / maximo}%`;
    contenedor.querySelector('[data-fill="meta"]').style.width = pendiente ? "0%" : `${100 * d.meta / maximo}%`;
  };
  if (nuevo && !movimientoReducido()) {contenedor.getBoundingClientRect(); requestAnimationFrame(ajustar);} else ajustar();
}

function abrirDetalle(id) {
  const d = datos.find(item => item.id === id);
  if (!d) return;
  detalleActual = id;
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

document.querySelectorAll("[data-categoria]").forEach(boton => boton.addEventListener("click", () => {categoria = boton.dataset.categoria; pintarTarjetas();}));
document.querySelectorAll("[data-resumen]").forEach(boton => boton.addEventListener("click", () => filtrarEstado(boton.dataset.resumen)));
$("buscar").addEventListener("input", pintarTarjetas);
$("filtro-estado").addEventListener("change", () => {pintarTarjetas(); pintarTorta();});
$("limpiar").addEventListener("click", limpiar);
$("restablecer").addEventListener("click", limpiar);
$("comparar").addEventListener("change", pintarComparativo);
$("series-barras").addEventListener("change", pintarBarras);
$("imprimir").addEventListener("click", () => window.print());
$("abrir-comparado").addEventListener("click", evento => abrirDetalle(evento.currentTarget.dataset.id));
$("ver-comparacion").addEventListener("click", () => {
  $("detalle").close();
  $("comparar").value = detalleActual;
  pintarComparativo();
  $("comparativo").scrollIntoView({block: "start", behavior: "smooth"});
  $("comparar").focus({preventScroll: true});
});
$("detalle").addEventListener("click", evento => {
  const caja = $("detalle").getBoundingClientRect();
  if (evento.target === $("detalle") && (evento.clientX < caja.left || evento.clientX > caja.right || evento.clientY < caja.top || evento.clientY > caja.bottom)) $("detalle").close();
});
const enlaces = [...document.querySelectorAll("nav a")];
if ("IntersectionObserver" in window) {
  const observador = new IntersectionObserver(entradas => {
    const visibles = entradas.filter(e => e.isIntersecting).sort((a,b) => b.intersectionRatio - a.intersectionRatio);
    if (!visibles.length) return;
    enlaces.forEach(enlace => {
      if (enlace.hash === "#" + visibles[0].target.id) enlace.setAttribute("aria-current", "location");
      else enlace.removeAttribute("aria-current");
    });
  }, {rootMargin: "-3% 0px -35% 0px", threshold: [0, 0.25, 0.5]});
  ["inicio", "graficos", "indicadores", "comparativo"].forEach(id => observador.observe($(id)));
}
$("vista-torta").addEventListener("change", () => {seleccionTorta = null; pintarTorta();});
$("reiniciar-torta").addEventListener("click", () => {seleccionTorta = null; $("vista-torta").value = "estados"; limpiar();});
$("torta-accion").addEventListener("click", () => {
  const modelo = modeloTorta();
  if (modelo.indicador) {
    $("comparar").value = modelo.indicador.id;
    pintarComparativo();
    $("comparativo").scrollIntoView({block: "start", behavior: "smooth"});
    $("comparar").focus({preventScroll: true});
  } else {
    $("indicadores").scrollIntoView({block: "start", behavior: "smooth"});
    $("indicadores-titulo").focus({preventScroll: true});
  }
});
pintarResumen();
pintarTarjetas();
pintarTorta();
pintarBarras();
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

