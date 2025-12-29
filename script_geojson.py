#!/usr/bin/env python3
"""
SCRIPT DE DESCARGA AUTOMÁTICA MULTIRIESGO
Descarga datos de Multiriesgo y los convierte a GeoJSON robusto
"""

import os
import time
import pandas as pd
import geopandas as gpd
import json
import re
import traceback
from datetime import datetime
from shapely.geometry import shape
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("🌱 SCRIPT DE DESCARGA AUTOMÁTICA MULTIRIESGO")
print("=" * 70)

# --- CONFIGURACIÓN DESDE SECRETS ---
USUARIO = os.getenv('MULTIRIESGO_USUARIO')
CLAVE = os.getenv('MULTIRIESGO_CONTRASENA')

if not USUARIO or not CLAVE:
    print("❌ Error: No se encontraron las credenciales en los Secrets.")
    exit(1)

# ============================================
# FUNCIONES DE PROCESAMIENTO (DE TU CÓDIGO COLAB)
# ============================================

def reparar_json_truncado(json_str):
    """
    Repara un JSON que fue truncado por Excel
    """
    if not isinstance(json_str, str):
        return json_str
    
    json_str = json_str.strip()
    
    # Caso 1: Termina con "..."
    if json_str.endswith('...'):
        print("   Detectado truncamiento '...', reparando...")
        last_valid = json_str.rfind('"}}')
        if last_valid != -1:
            return json_str[:last_valid + 3]
    
    # Caso 2: No termina correctamente
    elif not (json_str.endswith('}}') or json_str.endswith('}]}') or 
              json_str.endswith('}}}') or json_str.endswith('}]}}')):
        print("   JSON no termina correctamente, reparando...")
        
        patterns = [
            (r'\}\}\]\}$', 4),
            (r'\}\}\}$', 3),
            (r'\}\]\}$', 3),
            (r'\}\}$', 2),
        ]
        
        for pattern, length in patterns:
            match = re.search(pattern, json_str)
            if match:
                return json_str
        
        # Buscar último cierre válido
        for end_pattern in ['}}]}', '}}}', '}]}', '}}']:
            pos = json_str.rfind(end_pattern)
            if pos != -1:
                return json_str[:pos + len(end_pattern)]
    
    return json_str

def cargar_geojson_seguro(geojson_data, idx):
    """
    Carga GeoJSON de forma segura
    """
    resultados = {
        'geodata': None,
        'estado': 'ok',
        'mensaje': ''
    }
    
    try:
        if isinstance(geojson_data, str):
            # Intentar parsear directamente
            try:
                geodata = json.loads(geojson_data)
                resultados['geodata'] = geodata
                return resultados
            except json.JSONDecodeError:
                resultados['estado'] = 'reparando'
                
                # Reparar JSON truncado
                json_reparado = reparar_json_truncado(geojson_data)
                
                if json_reparado != geojson_data:
                    try:
                        geodata = json.loads(json_reparado)
                        resultados['geodata'] = geodata
                        resultados['estado'] = 'reparado'
                        return resultados
                    except:
                        pass
                
                # Extraer geometría manualmente
                coord_pattern = r'\[-?\d+\.\d+\s*,\s*-?\d+\.\d+\]'
                coords = re.findall(coord_pattern, geojson_data[:10000])
                
                if coords:
                    coords_list = []
                    for coord_str in coords[:20]:
                        try:
                            clean_coord = coord_str.replace(' ', '')
                            lat_lon = json.loads(clean_coord)
                            coords_list.append(lat_lon)
                        except:
                            continue
                    
                    if len(coords_list) >= 3:
                        geodata = {
                            "type": "FeatureCollection",
                            "features": [{
                                "type": "Feature",
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [coords_list + [coords_list[0]]]
                                },
                                "properties": {
                                    "lot": {"id": idx},
                                    "warning": "GEOMETRÍA RECUPERADA"
                                }
                            }]
                        }
                        resultados['geodata'] = geodata
                        resultados['estado'] = 'recuperado'
                        return resultados
                
                resultados['estado'] = 'error'
                return resultados
        else:
            resultados['geodata'] = geojson_data
            return resultados
            
    except Exception as e:
        resultados['estado'] = 'error'
        resultados['mensaje'] = str(e)[:100]
        return resultados

def procesar_dataframe(df, columna_geojson='POLIGONO'):
    """
    Procesa el DataFrame descargado y convierte a GeoJSON robusto
    """
    print(f"🔄 Procesando {len(df)} polígonos...")
    
    features = []
    errores = 0
    exitosas = 0
    
    for idx, row in df.iterrows():
        try:
            # Obtener datos GeoJSON
            geojson_data = row[columna_geojson] if columna_geojson in row else None
            
            if pd.isna(geojson_data):
                errores += 1
                continue
            
            # Cargar GeoJSON de forma segura
            resultado = cargar_geojson_seguro(geojson_data, idx)
            geodata = resultado['geodata']
            
            if not geodata:
                errores += 1
                continue
            
            # EXTRAER GEOMETRÍA
            geometry = None
            
            # CASO 1: FeatureCollection
            if isinstance(geodata, dict) and 'type' in geodata and geodata['type'] == 'FeatureCollection':
                if 'features' in geodata and len(geodata['features']) > 0:
                    feature = geodata['features'][0]
                    if 'geometry' in feature:
                        geometry = shape(feature['geometry'])
            
            if geometry is None:
                errores += 1
                continue
            
            # PREPARAR PROPIEDADES
            props_final = {}
            
            # Agregar TODAS las columnas del DataFrame
            for col in df.columns:
                if col != columna_geojson:
                    valor = row[col]
                    
                    if pd.isna(valor):
                        props_final[col] = None
                    elif isinstance(valor, (pd.Timestamp, datetime)):
                        props_final[col] = valor.strftime('%Y-%m-%d')
                    elif isinstance(valor, (dict, list)):
                        props_final[col] = str(valor)[:100]
                    else:
                        props_final[col] = valor
            
            # Agregar metadatos
            props_final['excel_fila_num'] = idx + 1
            props_final['procesado_en'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            props_final['estado_procesamiento'] = resultado['estado']
            
            # CREAR FEATURE
            feature_gdf = {
                "type": "Feature",
                "geometry": geometry.__geo_interface__,
                "properties": props_final
            }
            
            features.append(feature_gdf)
            exitosas += 1
            
        except Exception as e:
            errores += 1
            continue
    
    print(f"📊 Resultado: {exitosas} exitosas, {errores} errores")
    
    if features:
        # Crear GeoDataFrame
        feature_collection = {
            "type": "FeatureCollection",
            "features": features
        }
        
        gdf = gpd.GeoDataFrame.from_features(feature_collection)
        gdf.crs = "EPSG:4326"
        
        return gdf
    else:
        return None

# ============================================
# FUNCIÓN PRINCIPAL DE DESCARGA
# ============================================

def ejecutar_proceso():
    print("🚀 Iniciando proceso de descarga...")
    
    # Configurar Chrome para GitHub Actions
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Carpeta de descarga
    prefs = {"download.default_directory": os.getcwd()}
    chrome_options.add_experimental_option("prefs", prefs)

    try:
        # Inicializar Chrome
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=chrome_options
        )
        
        # 1. LOGIN
        print("🔐 Iniciando sesión en Multiriesgo...")
        driver.get("https://www.multiriesgo.com.ar/m-multiriesgo/login.aspx")
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "txtUsuario"))
        ).send_keys(USUARIO)
        
        driver.find_element(By.ID, "txtPassword").send_keys(CLAVE)
        driver.find_element(By.ID, "btnAceptar").click()
        
        time.sleep(5)
        
        # 2. DESCARGAR REPORTE
        print("📥 Navegando al reporte 173...")
        driver.get("https://www.multiriesgo.com.ar/m-multiriesgo/Reportes/Consultas_Reporte_Dinamico.aspx?ID_REPORTE=173")
        
        btn_excel = WebDriverWait(driver, 25).until(
            EC.element_to_be_clickable((By.ID, "btnExportarExcel"))
        )
        btn_excel.click()
        
        print("⏳ Esperando descarga...")
        time.sleep(30)  # Tiempo extra para descarga
        
        # 3. BUSCAR ARCHIVO DESCARGADO
        archivos = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.csv')]
        
        if not archivos:
            print("❌ Error: No se descargó ningún archivo")
            driver.quit()
            return False
        
        archivo_descargado = archivos[0]
        print(f"📦 Archivo detectado: {archivo_descargado}")
        
        # 4. LEER DATOS
        if archivo_descargado.endswith('.xlsx'):
            df = pd.read_excel(archivo_descargado)
        else:
            df = pd.read_csv(archivo_descargado, encoding='latin-1')
        
        print(f"📊 Datos cargados: {len(df)} filas, {len(df.columns)} columnas")
        print("📋 Columnas encontradas:")
        for col in df.columns.tolist():
            print(f"   • {col}")
        
        # 5. BUSCAR COLUMNA DE GEOMETRÍA
        columna_geojson = None
        posibles_nombres = ['POLIGONO', 'GEOJSON', 'geojson', 'GeoJSON', 'geometry', 'GEOMETRIA']
        
        for nombre in posibles_nombres:
            if nombre in df.columns:
                columna_geojson = nombre
                break
        
        if not columna_geojson:
            print("⚠️  No se encontró columna de polígonos. Usando primera columna que parezca JSON...")
            for col in df.columns:
                sample = str(df[col].iloc[0]) if len(df) > 0 else ""
                if 'coordinates' in sample or 'geometry' in sample or 'FeatureCollection' in sample:
                    columna_geojson = col
                    print(f"   → Detectada columna '{col}' por contenido")
                    break
        
        if not columna_geojson:
            print("❌ ERROR: No se encontró columna con datos GeoJSON")
            driver.quit()
            return False
        
        print(f"✅ Columna de polígonos: '{columna_geojson}'")
        
        # 6. PROCESAR DATOS
        gdf = procesar_dataframe(df, columna_geojson)
        
        if gdf is not None and len(gdf) > 0:
            # 7. GUARDAR GEOJSON
            output_file = "poligonos.geojson"
            gdf.to_file(output_file, driver='GeoJSON')
            
            print(f"\n✅ GeoJSON creado exitosamente: {output_file}")
            print(f"   • Polígonos: {len(gdf)}")
            print(f"   • Columnas: {len(gdf.columns)}")
            print(f"   • Tamaño: {os.path.getsize(output_file) / 1024 / 1024:.2f} MB")
            
            # 8. LIMPIAR ARCHIVOS TEMPORALES
            try:
                if os.path.exists(archivo_descargado):
                    os.remove(archivo_descargado)
                    print(f"🧹 Archivo temporal eliminado: {archivo_descargado}")
            except:
                pass
            
            driver.quit()
            return True
        else:
            print("❌ ERROR: No se pudieron procesar los datos")
            driver.quit()
            return False
        
    except Exception as e:
        print(f"❌ Error durante el proceso: {str(e)}")
        print(traceback.format_exc())
        try:
            driver.quit()
        except:
            pass
        return False

# ============================================
# EJECUCIÓN
# ============================================

if __name__ == "__main__":
    start_time = datetime.now()
    print(f"⏰ Inicio: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = ejecutar_proceso()
    
    end_time = datetime.now()
    elapsed = end_time - start_time
    
    print(f"\n{'='*70}")
    print(f"⏰ Duración total: {elapsed.total_seconds():.1f} segundos")
    print(f"🏁 Fin: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
        exit(0)
    else:
        print("❌ PROCESO FALLÓ")
        exit(1)
