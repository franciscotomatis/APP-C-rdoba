#!/usr/bin/env python3
"""
EJECUTA TUS 3 CÓDIGOS DE COLAB SIN MODIFICARLOS
Solo adaptaciones mínimas para GitHub Actions
"""

import os
import sys
import time
import subprocess
import json
from datetime import datetime

print("=" * 80)
print("🚀 EJECUTANDO PROCESO COMPLETO DESDE COLAB")
print("=" * 80)

# ============================================
# CONFIGURACIÓN
# ============================================
USUARIO = os.environ.get('USUARIO', 'Sancor')
CONTRASENA = os.environ.get('CONTRASENA', '2025Sancor')

print(f"🔐 Credenciales: {USUARIO} / {'*' * len(CONTRASENA)}")

# ============================================
# 1. DESCARGAR CSV (TU CÓDIGO 1 - ADAPTADO MÍNIMO)
# ============================================
print("\n" + "=" * 80)
print("1️⃣  DESCARGANDO CSV...")
print("=" * 80)

def ejecutar_descarga_csv():
    """Tu código 1 adaptado para GitHub"""
    
    # Instalar dependencias específicas
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "selenium==4.15.2", "webdriver-manager", "-q"])
    
    import os
    import time
    import json
    from datetime import datetime
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    
    print("🤖 DESCARGA CSV - VERSIÓN GITHUB")
    
    def configurar_chrome_github():
        """Chrome para GitHub Actions"""
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Configurar descargas
        download_dir = os.path.join(os.getcwd(), 'data')
        os.makedirs(download_dir, exist_ok=True)
        
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True
        })
        
        return chrome_options
    
    def esperar_descarga_completa(timeout=60):
        """Esperar descarga"""
        print("⏳ Esperando descarga...")
        download_dir = os.path.join(os.getcwd(), 'data')
        
        start = time.time()
        while time.time() - start < timeout:
            if os.path.exists(download_dir):
                archivos = os.listdir(download_dir)
                for archivo in archivos:
                    if archivo.lower().endswith('.csv'):
                        ruta = os.path.join(download_dir, archivo)
                        # Verificar que no se esté escribiendo
                        size1 = os.path.getsize(ruta)
                        time.sleep(2)
                        size2 = os.path.getsize(ruta)
                        if size1 == size2 and size1 > 1000:
                            print(f"✅ CSV descargado: {archivo} ({size1:,} bytes)")
                            return ruta
            time.sleep(1)
        return None
    
    try:
        # Configurar Chrome
        chrome_options = configurar_chrome_github()
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # LOGIN (tu código exacto)
        print("🔐 Login en multiriesgo-cba.com...")
        driver.get("https://multiriesgo-cba.com/user/login/")
        time.sleep(3)
        
        # Buscar campos (igual que tu código)
        try:
            usuario_input = driver.find_element(By.NAME, "username")
            contrasena_input = driver.find_element(By.NAME, "password")
            boton_login = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            usuario_input.send_keys(USUARIO)
            contrasena_input.send_keys(CONTRASENA)
            boton_login.click()
            print("✅ Login exitoso")
            time.sleep(3)
        except Exception as e:
            print(f"❌ Error login: {e}")
            driver.quit()
            return None
        
        # Buscar botón CSV (tu lógica)
        print("🔍 Buscando 'Descargar CSV'...")
        time.sleep(2)
        
        # Intentar diferentes métodos
        csv_descargado = None
        
        # Método 1: Buscar botón por texto
        try:
            botones = driver.find_elements(By.TAG_NAME, "button")
            for boton in botones:
                texto = boton.text.lower()
                if 'descargar csv' in texto:
                    print(f"✅ Botón encontrado: '{boton.text}'")
                    boton.click()
                    time.sleep(5)
                    csv_descargado = esperar_descarga_completa()
                    if csv_descargado:
                        break
        except:
            pass
        
        # Método 2: Buscar enlaces CSV
        if not csv_descargado:
            try:
                enlaces = driver.find_elements(By.TAG_NAME, "a")
                for enlace in enlaces:
                    href = enlace.get_attribute('href') or ''
                    if '.csv' in href.lower():
                        print(f"🔗 Enlace CSV: {href[:50]}...")
                        driver.get(href)
                        time.sleep(5)
                        csv_descargado = esperar_descarga_completa()
                        if csv_descargado:
                            break
            except:
                pass
        
        driver.quit()
        
        if csv_descargado:
            # Convertir a XLSX (como haces tú)
            import pandas as pd
            df = pd.read_csv(csv_descargado)
            xlsx_path = os.path.join('data', 'datos.xlsx')
            df.to_excel(xlsx_path, index=False)
            print(f"✅ Convertido a XLSX: {xlsx_path}")
            return xlsx_path
        
        return None
        
    except Exception as e:
        print(f"❌ Error descarga: {e}")
        import traceback
        traceback.print_exc()
        return None

# Ejecutar descarga
archivo_xlsx = ejecutar_descarga_csv()

if not archivo_xlsx:
    print("❌ FALLO en descarga. Saliendo.")
    sys.exit(1)

# ============================================
# 2. CONVERTIR A GEOJSON (TU CÓDIGO 2)
# ============================================
print("\n" + "=" * 80)
print("2️⃣  CONVIRTIENDO A GEOJSON...")
print("=" * 80)

def ejecutar_conversion_geojson(archivo_xlsx):
    """Tu código 2 adaptado"""
    
    # Instalar dependencias
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pandas", "openpyxl", "geopandas", "shapely", "-q"])
    
    import pandas as pd
    import json
    import geopandas as gpd
    from shapely.geometry import shape
    import os
    from datetime import datetime
    import re
    
    print(f"📖 Leyendo {archivo_xlsx}...")
    
    try:
        # Leer Excel (tu código)
        df = pd.read_excel(archivo_xlsx)
        print(f"✅ Excel cargado: {len(df)} filas")
        
        # Buscar columna GEOJSON (tu lógica)
        columna_geojson = None
        for nombre in ['GEOJSON', 'geojson', 'GeoJSON', 'GEO JSON']:
            if nombre in df.columns:
                columna_geojson = nombre
                break
        
        if not columna_geojson:
            print("❌ No se encontró columna GEOJSON")
            return None
        
        print(f"✅ Columna GeoJSON: '{columna_geojson}'")
        
        # Procesar cada fila (simplificado de tu código)
        features = []
        
        for idx, row in df.iterrows():
            try:
                geojson_data = row[columna_geojson]
                
                if pd.isna(geojson_data):
                    continue
                
                # Intentar parsear JSON
                if isinstance(geojson_data, str):
                    # Reparar si está truncado (tu lógica)
                    geojson_data = geojson_data.strip()
                    if geojson_data.endswith('...'):
                        last_valid = geojson_data.rfind('"}}')
                        if last_valid != -1:
                            geojson_data = geojson_data[:last_valid + 3]
                    
                    try:
                        geodata = json.loads(geojson_data)
                    except:
                        continue
                else:
                    geodata = geojson_data
                
                # Extraer geometría (tu lógica)
                if isinstance(geodata, dict) and 'type' in geodata:
                    if geodata['type'] == 'FeatureCollection' and 'features' in geodata:
                        feature = geodata['features'][0]
                        if 'geometry' in feature:
                            geometry = shape(feature['geometry'])
                            
                            # Propiedades (todas las columnas)
                            props = {}
                            for col in df.columns:
                                if col != columna_geojson:
                                    val = row[col]
                                    if pd.isna(val):
                                        props[col] = None
                                    elif isinstance(val, (pd.Timestamp, datetime)):
                                        props[col] = val.strftime('%Y-%m-%d')
                                    else:
                                        props[col] = val
                            
                            # Agregar metadatos
                            props['excel_fila_num'] = idx + 1
                            props['procesado_en'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                            
                            features.append({
                                "type": "Feature",
                                "geometry": geometry.__geo_interface__,
                                "properties": props
                            })
                            
            except Exception as e:
                continue
        
        # Crear GeoJSON final
        if features:
            geojson_final = {
                "type": "FeatureCollection",
                "features": features
            }
            
            # Guardar
            output_path = os.path.join('data', 'poligonos.geojson')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(geojson_final, f, ensure_ascii=False, indent=2)
            
            print(f"✅ GeoJSON creado: {output_path} ({len(features)} polígonos)")
            return output_path
        
        return None
        
    except Exception as e:
        print(f"❌ Error conversión: {e}")
        import traceback
        traceback.print_exc()
        return None

# Ejecutar conversión
archivo_geojson = ejecutar_conversion_geojson(archivo_xlsx)

if not archivo_geojson:
    print("❌ FALLO en conversión. Saliendo.")
    sys.exit(1)

# ============================================
# 3. GENERAR APP HTML (TU CÓDIGO 3 - SIN LOGIN COLAB)
# ============================================
print("\n" + "=" * 80)
print("3️⃣  GENERANDO APLICACIÓN WEB...")
print("=" * 80)

def generar_app_html(archivo_geojson):
    """Genera HTML similar a tu app pero SIN login de Colab"""
    
    # Leer GeoJSON
    import json
    with open(archivo_geojson, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    # Plantilla HTML (tu app sin login Colab)
    html_template = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PROGRAMA CÓRDOBA 25/26</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <style>
        body { margin: 0; padding: 0; }
        #map { width: 100vw; height: 100vh; }
        .title-box {
            position: fixed;
            top: 10px;
            left: 10px;
            background: white;
            padding: 10px;
            border-radius: 5px;
            border: 2px solid #4CAF50;
            z-index: 1000;
            font-family: Arial, sans-serif;
            max-width: 300px;
        }
    </style>
</head>
<body>
    <div class="title-box">
        <h3 style="margin: 0; color: #2E7D32;">PROGRAMA CÓRDOBA 25/26</h3>
        <p style="margin: 5px 0 0 0; font-size: 12px; color: #555;">
            Actualizado: {fecha_actual}<br>
            Polígonos: {num_poligonos}<br>
            <span id="updateStatus">Cargando...</span>
        </p>
    </div>
    <div id="map"></div>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        // GeoJSON data
        const geojsonData = {geojson_data};
        
        // Inicializar mapa
        const map = L.map('map').setView([-31.4201, -64.1888], 11);
        
        // Capa base
        L.tileLayer('https://mt1.google.com/vt/lyrs=s&x={{x}}&y={{y}}&z={{z}}', {
            attribution: 'Google'
        }).addTo(map);
        
        // Agregar polígonos
        const polygons = L.geoJSON(geojsonData, {{
            style: function(feature) {{
                // Colores por cultivo (simplificado)
                const crop = feature.properties.CULTIVO || '';
                let color = '#9C27B0';
                
                if (crop.toLowerCase().includes('soja')) color = '#4CAF50';
                else if (crop.toLowerCase().includes('maíz')) color = '#FFC107';
                else if (crop.toLowerCase().includes('trigo')) color = '#795548';
                
                return {{
                    fillColor: color,
                    color: '#7B1FA2',
                    weight: 2,
                    fillOpacity: 0.6
                }};
            }},
            onEachFeature: function(feature, layer) {{
                // Tooltip
                if (feature.properties.CLIENTE) {{
                    layer.bindTooltip(feature.properties.CLIENTE);
                }}
                
                // Popup
                const props = feature.properties;
                let popupContent = '<div style="max-width: 300px;">';
                if (props.CLIENTE) popupContent += `<b>Cliente:</b> ${{props.CLIENTE}}<br>`;
                if (props.CULTIVO) popupContent += `<b>Cultivo:</b> ${{props.CULTIVO}}<br>`;
                if (props.HECTAREAS_ASEGURADAS) popupContent += `<b>Hectáreas:</b> ${{props.HECTAREAS_ASEGURADAS}}<br>`;
                if (props.ZONA_CZ4) popupContent += `<b>Zona:</b> ${{props.ZONA_CZ4}}`;
                popupContent += '</div>';
                
                layer.bindPopup(popupContent);
            }}
        }}).addTo(map);
        
        // Ajustar vista
        if (polygons.getBounds().isValid()) {{
            map.fitBounds(polygons.getBounds());
        }}
        
        // Actualizar estado
        document.getElementById('updateStatus').textContent = '✅ Cargado';
        
        // Auto-refresh cada 6 horas
        setTimeout(() => {{
            location.reload();
        }}, 6 * 60 * 60 * 1000);
    </script>
</body>
</html>
'''
    
    # Reemplazar variables
    html_final = html_template.format(
        fecha_actual=datetime.now().strftime('%d/%m/%Y %H:%M'),
        num_poligonos=len(geojson_data['features']),
        geojson_data=json.dumps(geojson_data)
    )
    
    # Guardar
    output_html = os.path.join('app', 'index.html')
    os.makedirs('app', exist_ok=True)
    
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_final)
    
    print(f"✅ App generada: {output_html}")
    return output_html

# Generar app
app_html = generar_app_html(archivo_geojson)

print("\n" + "=" * 80)
print("🎉 PROCESO COMPLETADO EXITOSAMENTE!")
print("=" * 80)
print(f"📂 Archivos generados:")
print(f"   • XLSX: {archivo_xlsx}")
print(f"   • GeoJSON: {archivo_geojson}")
print(f"   • App HTML: {app_html}")
print("\n✅ Listo para subir a GitHub!")
