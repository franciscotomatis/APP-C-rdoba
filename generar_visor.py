import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import Fullscreen, MeasureControl
import json
import os
import hashlib

# ==========================================
# 1. SEGURIDAD (SECRETS DE GITHUB)
# ==========================================
USUARIO_CORRECTO = os.getenv('MULTIRIESGO_USUARIO')
CONTRASENA_CORRECTA = os.getenv('MULTIRIESGO_CONTRASENA')

def generar_hash_js(texto):
    salt = "ProgramaCordoba25/26-SancorSeguro"
    return hashlib.sha256((texto + salt).encode()).hexdigest()[:16]

HASH_USUARIO = generar_hash_js(USUARIO_CORRECTO)
HASH_CONTRASENA = generar_hash_js(CONTRASENA_CORRECTA)

def crear_app():
    # Buscamos el archivo generado por tu otro script
    input_file = "poligonos.geojson"
    if not os.path.exists(input_file):
        print("❌ Error: poligonos.geojson no encontrado.")
        return

    # Carga y Proyección
    gdf = gpd.read_file(input_file).to_crs(epsg=4326)

    # Identificación de campos (basado en tu reporte de Multiriesgo)
    c_cultivo = next((c for c in gdf.columns if c.lower() in ['cultivo', 'producto']), "CULTIVO")
    c_ha = next((c for c in gdf.columns if c.lower() in ['hectareas', 'has']), "HECTAREAS")
    c_cliente = next((c for c in gdf.columns if c.lower() in ['cliente', 'nombre']), "CLIENTE")
    c_zona = next((c for c in gdf.columns if c.lower() in ['zona', 'region']), "ZONA")

    # Cálculos Estadísticos
    gdf[c_ha] = pd.to_numeric(gdf[c_ha], errors='coerce').fillna(0)
    hectareas_por_zona = gdf.groupby(c_zona)[c_ha].sum().to_dict()
    proyectado = {"1": 125257, "2": 228948, "3": 233990, "4": 198450}
    
    # Datos para Buscador JS
    lista_busqueda = []
    for _, row in gdf.iterrows():
        b = row.geometry.bounds
        lista_busqueda.append({
            "n": str(row[c_cliente]),
            "t": str(row[c_cultivo]),
            "h": round(float(row[c_ha]), 1),
            "b": [[b[1], b[0]], [b[3], b[2]]]
        })

    # --- MAPA ---
    m = folium.Map(location=[-31.4, -64.2], zoom_start=7, tiles=None)
    folium.TileLayer('OpenStreetMap', name='Mapa Calles').add_to(m)
    folium.TileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='Satélite').add_to(m)
    folium.TileLayer('CartoDB positron', name='Mapa Claro').add_to(m)

    def style_fn(f):
        cul = str(f['properties'].get(c_cultivo, '')).lower()
        color = '#4CAF50' if 'soja' in cul else '#FFC107' if 'maiz' in cul or 'maíz' in cul else '#795548' if 'trigo' in cul else '#9C27B0'
        return {'fillColor': color, 'color': 'white', 'weight': 1, 'fillOpacity': 0.6}

    folium.GeoJson(gdf, style_function=style_fn, 
                   tooltip=folium.GeoJsonTooltip(fields=[c_cliente, c_cultivo, c_ha])).add_to(m)
    
    Fullscreen().add_to(m)
    MeasureControl(position='topright').add_to(m)

    # --- GENERACIÓN DE TABLA DINÁMICA ---
    filas = ""
    for z in sorted(proyectado.keys()):
        real = hectareas_por_zona.get(z, 0)
        proy = proyectado[z]
        dif = real - proy
        perc = (dif/proy*100) if proy > 0 else 0
        icono = "🟢" if dif >= 0 else "🔴"
        filas += f"<tr><td>Zona {z}</td><td>{real:,.0f}</td><td>{proy:,.0f}</td><td style='color:{'green' if dif>=0 else 'red'}'>{dif:+,.0f}</td><td>{perc:.1f}% {icono}</td></tr>"

    # --- HTML / JS COMPLETO (IDENTICO A LAS 7 PARTES) ---
    html_app = f"""
    <style>
        @keyframes shake {{ 0%, 100% {{ transform: translateX(0); }} 20%, 60% {{ transform: translateX(-5px); }} 40%, 80% {{ transform: translateX(5px); }} }}
        #loginScreen {{ position:fixed; top:0; left:0; width:100%; height:100%; background:#f8f9fa; z-index:20000; display:flex; align-items:center; justify-content:center; font-family:Arial; }}
        .login-box {{ background:white; padding:40px; border-radius:15px; box-shadow:0 15px 35px rgba(0,0,0,0.2); width:350px; text-align:center; border-top: 5px solid #2E7D32; }}
        #lupitaBuscador {{ position:fixed; top:20px; left:60px; z-index:9999; background:white; padding:15px; border-radius:8px; width:280px; box-shadow:0 4px 12px rgba(0,0,0,0.15); display:none; }}
        #btnGraficos {{ position:fixed; bottom:30px; left:30px; background:#2E7D32; color:white; width:60px; height:60px; border-radius:50%; display:none; align-items:center; justify-content:center; font-size:28px; cursor:pointer; z-index:9997; box-shadow:0 4px 15px rgba(0,0,0,0.3); }}
        #panelGraficos {{ position:fixed; bottom:-100%; left:0; width:100%; height:85%; background:white; z-index:10001; transition:0.5s ease-in-out; overflow-y:auto; font-family:Arial; border-radius:25px 25px 0 0; }}
        .tabla-resumen {{ width:90%; margin:20px auto; border-collapse:collapse; font-size: 14px; }}
        .tabla-resumen th, .tabla-resumen td {{ padding:12px; border-bottom:1px solid #eee; text-align:center; }}
        .tabla-resumen th {{ background:#f1f8e9; color:#2E7D32; }}
    </style>

    <div id="loginScreen">
        <div class="login-box" id="lbox">
            <img src="https://www.sancorseguros.com.ar/images/logo-sancor-seguros.png" style="width:180px; margin-bottom:20px;">
            <h3 style="color:#2E7D32; margin-top:0;">PROGRAMA CÓRDOBA</h3>
            <input type="text" id="lu" placeholder="Usuario" style="width:100%; padding:12px; margin-bottom:15px; border:1px solid #ddd; border-radius:5px;">
            <input type="password" id="lp" placeholder="Contraseña" style="width:100%; padding:12px; margin-bottom:20px; border:1px solid #ddd; border-radius:5px;">
            <button onclick="checkLogin()" style="width:100%; padding:12px; background:#2E7D32; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">INGRESAR</button>
            <p id="lerr" style="color:red; font-size:12px; margin-top:15px; display:none;">❌ Credenciales incorrectas</p>
        </div>
    </div>

    <div id="lupitaBuscador">
        <input type="text" id="ib" placeholder="🔍 Buscar productor..." style="width:100%; padding:10px; border:1px solid #ccc; border-radius:4px;">
        <div id="rb" style="max-height:250px; overflow-y:auto; margin-top:10px;"></div>
    </div>

    <div id="btnGraficos" onclick="tgP()">📊</div>

    <div id="panelGraficos">
        <div style="background:#2E7D32; color:white; padding:20px; display:flex; justify-content:space-between; align-items:center; position:sticky; top:0;">
            <h2 style="margin:0;">Dashboard de Cumplimiento</h2>
            <span onclick="tgP()" style="cursor:pointer; font-size:35px;">&times;</span>
        </div>
        <table class="tabla-resumen">
            <thead><tr><th>Zona</th><th>Real (ha)</th><th>Proyectado</th><th>Diferencia</th><th>% Var</th></tr></thead>
            <tbody>{filas}</tbody>
        </table>
    </div>

    <script>
        const CLIENTES = {json.dumps(lista_busqueda)};
        const HU = "{HASH_USUARIO}";
        const HP = "{HASH_CONTRASENA}";

        async function getH(t) {{
            const s = "ProgramaCordoba25/26-SancorSeguro";
            const m = new TextEncoder().encode(t + s);
            const b = await crypto.subtle.digest('SHA-256', m);
            return Array.from(new Uint8Array(b)).map(b => b.toString(16).padStart(2,'0')).join('').substring(0,16);
        }}

        async function checkLogin() {{
            const u = await getH(document.getElementById('lu').value);
            const p = await getH(document.getElementById('lp').value);
            if(u === HU && p === HP) {{
                document.getElementById('loginScreen').style.display = 'none';
                document.getElementById('lupitaBuscador').style.display = 'block';
                document.getElementById('btnGraficos').style.display = 'flex';
            }} else {{
                document.getElementById('lerr').style.display = 'block';
                document.getElementById('lbox').style.animation = 'shake 0.5s';
                setTimeout(() => document.getElementById('lbox').style.animation = '', 500);
            }}
        }}

        document.getElementById('ib').addEventListener('input', function(e) {{
            const t = e.target.value.toLowerCase();
            const r = document.getElementById('rb');
            r.innerHTML = '';
            if(t.length < 3) return;
            CLIENTES.filter(c => c.n.toLowerCase().includes(t)).forEach(c => {{
                const d = document.createElement('div');
                d.style.padding = '10px; border-bottom: 1px solid #eee; cursor:pointer;';
                d.innerHTML = `<b>${{c.n}}</b><br><small>${{c.t}} - ${{c.h}} ha</small>`;
                d.onclick = () => {{ window[document.querySelector('.folium-map').id].fitBounds(c.b); }};
                r.appendChild(d);
            }});
        }});

        function tgP() {{
            const p = document.getElementById('panelGraficos');
            p.style.bottom = p.style.bottom === '0px' ? '-100%' : '0px';
        }}
    </script>
    """
    m.get_root().html.add_child(folium.Element(html_app))
    m.save("index.html")
    print("✅ App generada: index.html")

if __name__ == "__main__":
    crear_app()
