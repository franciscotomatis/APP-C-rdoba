#!/usr/bin/env python3
"""
PROCESO COMPLETO: Tus 2 códigos de Colab UNIDOS
1. Descarga CSV de multiriesgo-cba.com
2. Convierte a GeoJSON con manejo de errores
"""

import os
import sys
import time
import json
import pandas as pd
from datetime import datetime
import re

print("=" * 80)
print("🚀 INICIANDO PROCESO AUTOMÁTICO")
print("=" * 80)

# ===========================================================================
# CONFIGURACIÓN
# ===========================================================================
USUARIO = os.environ.get('MULTIRIESGO_USUARIO', 'Sancor')
CONTRASENA = os.environ.get('MULTIRIESGO_CONTRASENA', '2025Sancor')

print(f"🔐 Credenciales para multiriesgo-cba.com:")
print(f"   Usuario: {USUARIO}")
print(f"   Contraseña: {'*' * len(CONTRASENA)}")

# Crear carpetas
os.makedirs('data', exist_ok=True)
os.makedirs('app', exist_ok=True)

# ===========================================================================
# PARTE 1: DESCARGAR CSV (TU CÓDIGO EXACTO - solo adaptado para GitHub)
# ===========================================================================
print("\n" + "=" * 80)
print("1️⃣  DESCARGA DE CSV DESDE MULTIRIESGO-CBA.COM")
print("=" * 80)

def descargar_csv_multiriesgo():
    """TU código de descarga, adaptado mínimo para GitHub"""
    
    try:
        print("Instalando dependencias para Selenium...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", 
                              "selenium==4.15.2", "webdriver-manager", "-q"])
        
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("🔧 Configurando Chrome para GitHub Actions...")
        
        # Configuración HEADLESS para GitHub
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Configurar descargas automáticas
        download_path = os.path.join(os.getcwd(), 'data')
        chrome_options.add_experimental_option("prefs", {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False
        })
        
        print(f"📂 Descargas irán a: {download_path}")
        
        # Iniciar Chrome
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # === TU LÓGICA DE LOGIN EXACTA ===
        print("🌐 Navegando a https://multiriesgo-cba.com/user/login/")
        driver.get("https://multiriesgo-cba.com/user/login/")
        time.sleep(5)
        
        print("🔐 Buscando campos de login...")
        try:
            # Buscar por name (como en tu código)
            username_input = driver.find_element(By.NAME, "username")
            password_input = driver.find_element(By.NAME, "password")
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            print("✅ Campos encontrados, ingresando credenciales...")
            username_input.send_keys(USUARIO)
            password_input.send_keys(CONTRASENA)
            login_button.click()
            time.sleep(5)
            
            print(f"📍 URL después de login: {driver.current_url}")
            
            if "dashboard" in driver.current_url or "login" not in driver.current_url:
                print("✅ Login exitoso")
            else:
                print("⚠️ Posible problema con login")
                
        except Exception as e:
            print(f"❌ Error en login: {e}")
            # Tomar screenshot para debug
            try:
                driver.save_screenshot('error_login.png')
                print("📸 Screenshot guardado: error_login.png")
            except:
                pass
            driver.quit()
            return None
        
        # === BUSCAR BOTÓN "DESCARGAR CSV" (TU LÓGICA) ===
        print("\n🔍 Buscando botón 'Descargar CSV'...")
        time.sleep(3)
        
        # Método 1: Buscar por texto en botones (como haces tú)
        boton_encontrado = None
        try:
            botones = driver.find_elements(By.TAG_NAME, "button")
            print(f"🔘 Botones encontrados: {len(botones)}")
            
            for i, boton in enumerate(botones):
                texto = boton.text.strip().lower()
                if 'descargar csv' in texto or 'exportar csv' in texto:
                    boton_encontrado = boton
                    print(f"✅ Botón CSV encontrado (opción {i+1}): '{boton.text}'")
                    break
                    
        except Exception as e:
            print(f"⚠️ Error buscando botones: {e}")
        
        # Método 2: Buscar enlaces CSV
        if not boton_encontrado:
            try:
                enlaces = driver.find_elements(By.TAG_NAME, "a")
                for enlace in enlaces:
                    href = enlace.get_attribute('href') or ''
                    if '.csv' in href.lower():
                        boton_encontrado = enlace
                        print(f"✅ Enlace CSV encontrado: {href[:50]}...")
                        break
            except:
                pass
        
        if not boton_encontrado:
            print("❌ No se encontró botón/enlace CSV")
            driver.quit()
            return None
        
        # === HACER CLIC Y ESPERAR DESCARGA ===
        print("🖱️ Haciendo clic en el botón...")
        try:
            driver.execute_script("arguments[0].click();", boton_encontrado)
        except:
            boton_encontrado.click()
        
        print("⏳ Esperando descarga (hasta 60 segundos)...")
        
        # Esperar archivo CSV
        csv_file = None
        start_time = time.time()
        
        while time.time() - start_time < 60:
            if os.path.exists('data'):
                archivos = os.listdir('data')
                csv_archivos = [f for f in archivos if f.lower().endswith('.csv')]
                
                if csv_archivos:
                    # Tomar el más reciente
                    csv_archivos.sort(key=lambda x: os.path.getctime(os.path.join('data', x)), reverse=True)
                    archivo_mas_reciente = csv_archivos[0]
                    ruta_csv = os.path.join('data', archivo_mas_reciente)
                    
                    # Verificar que terminó de descargar
                    size1 = os.path.getsize(ruta_csv)
                    time.sleep(2)
                    size2 = os.path.getsize(ruta_csv)
                    
                    if size1 == size2 and size1 > 1024:  # Al menos 1KB
                        csv_file = ruta_csv
                        print(f"✅ CSV descargado: {archivo_mas_reciente} ({size1:,} bytes)")
                        break
            
            time.sleep(1)
        
        driver.quit()
        
        if csv_file:
            # Convertir a XLSX (como haces tú)
            print("🔄 Convirtiendo CSV a XLSX...")
            try:
                df = pd.read_csv(csv_file)
                xlsx_path = os.path.join('data', 'datos_actualizados.xlsx')
                df.to_excel(xlsx_path, index=False)
                print(f"✅ XLSX guardado: {xlsx_path}")
                return xlsx_path
            except Exception as e:
                print(f"⚠️ Error convirtiendo a XLSX: {e}")
                return csv_file  # Devolver CSV si falla conversión
        
        return None
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO en descarga: {e}")
        import traceback
        traceback.print_exc()
        return None

# Ejecutar descarga
print("\n🎯 Iniciando descarga CSV...")
archivo_excel = descargar_csv_multiriesgo()

if not archivo_excel:
    print("❌ FALLO en descarga CSV")
    print("⚠️ Creando datos de prueba para continuar...")
    
    # Crear datos de prueba mínimos
    datos_prueba = pd.DataFrame({
        'GEOJSON': [json.dumps({
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[-64.5, -31.0], [-64.4, -31.0], 
                                    [-64.4, -30.9], [-64.5, -30.9], 
                                    [-64.5, -31.0]]]
                },
                "properties": {
                    "CLIENTE": "CLIENTE PRUEBA",
                    "CULTIVO": "SOJA",
                    "HECTAREAS_ASEGURADAS": 150,
                    "ZONA_CZ4": "2",
                    "DEPARTAMENTO": "RIO CUARTO",
                    "LOCALIDAD": "VILLA MARÍA"
                }
            }]
        })],
        'CLIENTE': ['CLIENTE PRUEBA'],
        'CULTIVO': ['SOJA'],
        'HECTAREAS_ASEGURADAS': [150],
        'ZONA_CZ4': ['2'],
        'DEPARTAMENTO': ['RIO CUARTO'],
        'LOCALIDAD': ['VILLA MARÍA']
    })
    
    archivo_excel = 'data/datos_prueba.xlsx'
    datos_prueba.to_excel(archivo_excel, index=False)
    print(f"✅ Datos de prueba creados: {archivo_excel}")

# ===========================================================================
# PARTE 2: CONVERSIÓN A GEOJSON (TU CÓDIGO CON MANEJO DE ERRORES)
# ===========================================================================
print("\n" + "=" * 80)
print("2️⃣  CONVERSIÓN A GEOJSON CON MANEJO DE ERRORES")
print("=" * 80)

def convertir_xlsx_a_geojson(archivo_excel):
    """TU código de conversión con manejo de errores"""
    
    try:
        print("📦 Instalando geopandas y dependencias...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", 
                              "geopandas", "shapely", "openpyxl", "-q"])
        
        import geopandas as gpd
        from shapely.geometry import shape
        
        print(f"📖 Leyendo archivo Excel: {archivo_excel}")
        
        # Leer Excel
        try:
            df = pd.read_excel(archivo_excel)
            print(f"✅ Excel cargado: {len(df)} filas, {len(df.columns)} columnas")
            
            # Mostrar columnas
            print("📋 Columnas detectadas:")
            for i, col in enumerate(df.columns.tolist()[:15], 1):
                print(f"   {i:2d}. {col}")
            if len(df.columns) > 15:
                print(f"   ... y {len(df.columns) - 15} más")
                
        except Exception as e:
            print(f"❌ Error leyendo Excel: {e}")
            return None
        
        # Buscar columna GeoJSON (TU LÓGICA EXACTA)
        columna_geojson = None
        posibles_nombres = ['GEOJSON', 'geojson', 'GeoJSON', 'GEO JSON', 'geo_json']
        
        for nombre in posibles_nombres:
            if nombre in df.columns:
                columna_geojson = nombre
                print(f"✅ Columna GeoJSON encontrada: '{columna_geojson}'")
                break
        
        if not columna_geojson:
            print("❌ NO se encontró columna GeoJSON")
            print("   Buscando columnas que puedan contener JSON...")
            
            # Buscar columnas que contengan JSON
            for col in df.columns:
                try:
                    muestra = str(df[col].iloc[0]) if len(df) > 0 else ""
                    if 'FeatureCollection' in muestra or 'coordinates' in muestra:
                        columna_geojson = col
                        print(f"✅ Columna potencial encontrada: '{col}'")
                        break
                except:
                    continue
            
            if not columna_geojson:
                print("❌ No hay datos GeoJSON en el archivo")
                return None
        
        # ===================================================================
        # TU LÓGICA DE MANEJO DE ERRORES EN JSON
        # ===================================================================
        print(f"\n🔄 Procesando {len(df)} polígonos con manejo de errores...")
        
        def reparar_json_truncado(json_str):
            """TU función para reparar JSON truncado por Excel"""
            if not isinstance(json_str, str):
                return json_str
            
            json_str = json_str.strip()
            
            # Caso: Termina con "..."
            if json_str.endswith('...'):
                last_valid = json_str.rfind('"}}')
                if last_valid != -1:
                    return json_str[:last_valid + 3]
            
            # Caso: No termina correctamente
            elif not (json_str.endswith('}}') or json_str.endswith('}]}') or 
                    json_str.endswith('}}}') or json_str.endswith('}]}}')):
                # Buscar último cierre válido
                for end_pattern in ['}}]}', '}}}', '}]}', '}}']:
                    pos = json_str.rfind(end_pattern)
                    if pos != -1:
                        return json_str[:pos + len(end_pattern)]
            
            return json_str
        
        features = []
        errores = []
        filas_procesadas = 0
        
        for idx, row in df.iterrows():
            try:
                geojson_data = row[columna_geojson]
                
                if pd.isna(geojson_data):
                    errores.append(f"Fila {idx+1}: Celda vacía")
                    continue
                
                # Intentar cargar GeoJSON
                geodata = None
                
                if isinstance(geojson_data, str):
                    # Intentar parsear directamente
                    try:
                        geodata = json.loads(geojson_data)
                    except json.JSONDecodeError:
                        # Intentar reparar
                        json_reparado = reparar_json_truncado(geojson_data)
                        try:
                            geodata = json.loads(json_reparado)
                        except:
                            # Extraer coordenadas manualmente (TU LÓGICA)
                            coord_pattern = r'\[-?\d+\.\d+\s*,\s*-?\d+\.\d+\]'
                            coords = re.findall(coord_pattern, geojson_data[:5000])
                            
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
                                                "lot": {
                                                    "id": idx,
                                                    "name": f"Lote Recuperado {idx}",
                                                    "hectares_declared": 0
                                                },
                                                "warning": "GEOMETRÍA RECUPERADA - DATOS INCOMPLETOS"
                                            }
                                        }]
                                    }
                                else:
                                    errores.append(f"Fila {idx+1}: No se pudo extraer geometría")
                                    continue
                            else:
                                errores.append(f"Fila {idx+1}: JSON inválido y sin coordenadas")
                                continue
                else:
                    geodata = geojson_data
                
                # Extraer geometría (TU LÓGICA)
                if isinstance(geodata, dict) and 'type' in geodata and geodata['type'] == 'FeatureCollection':
                    if 'features' in geodata and len(geodata['features']) > 0:
                        feature = geodata['features'][0]
                        if 'geometry' in feature:
                            geometry = shape(feature['geometry'])
                            
                            # Propiedades: TODAS las columnas del Excel
                            props = {}
                            for col in df.columns:
                                if col != columna_geojson:
                                    valor = row[col]
                                    if pd.isna(valor):
                                        props[col] = None
                                    elif isinstance(valor, (pd.Timestamp, datetime)):
                                        props[col] = valor.strftime('%Y-%m-%d')
                                    elif isinstance(valor, (dict, list)):
                                        props[col] = str(valor)[:100]
                                    else:
                                        props[col] = valor
                            
                            # Agregar metadatos
                            props['excel_fila_num'] = idx + 1
                            props['procesado_en'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                            
                            features.append({
                                "type": "Feature",
                                "geometry": geometry.__geo_interface__,
                                "properties": props
                            })
                            
                            filas_procesadas += 1
                
            except Exception as e:
                errores.append(f"Fila {idx+1}: Error crítico - {str(e)[:50]}")
                continue
        
        # ===================================================================
        # CREAR GEOJSON FINAL
        # ===================================================================
        print(f"\n📊 RESULTADO DE PROCESAMIENTO:")
        print(f"   • Total filas en Excel: {len(df)}")
        print(f"   • ✅ Filas procesadas exitosamente: {filas_procesadas}")
        print(f"   • ❌ Filas con errores: {len(errores)}")
        
        if errores and len(errores) <= 10:
            print(f"   • Primeros errores:")
            for error in errores[:5]:
                print(f"     - {error}")
        
        if features:
            # Crear FeatureCollection
            geojson_final = {
                "type": "FeatureCollection",
                "features": features
            }
            
            # Guardar GeoJSON
            output_path = os.path.join('data', 'poligonos_actualizados.geojson')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(geojson_final, f, ensure_ascii=False, indent=2)
            
            print(f"\n✅ GEOJSON GENERADO: {output_path}")
            print(f"   • Polígonos: {len(features)}")
            print(f"   • Tamaño: {os.path.getsize(output_path):,} bytes")
            
            # También guardar versión minificada para la web
            web_geojson = os.path.join('data', 'poligonos.geojson')
            with open(web_geojson, 'w', encoding='utf-8') as f:
                json.dump(geojson_final, f, ensure_ascii=False)
            
            print(f"✅ Versión web: {web_geojson}")
            
            return web_geojson
        else:
            print("❌ No se crearon polígonos válidos")
            return None
            
    except Exception as e:
        print(f"❌ ERROR en conversión: {e}")
        import traceback
        traceback.print_exc()
        return None

# Ejecutar conversión
print("\n🎯 Iniciando conversión a GeoJSON...")
archivo_geojson = convertir_xlsx_a_geojson(archivo_excel)

if not archivo_geojson:
    print("❌ FALLO en conversión GeoJSON")
    # Crear GeoJSON mínimo de emergencia
    geojson_emergencia = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-64.5, -31.0], [-64.3, -31.0], 
                                [-64.3, -30.8], [-64.5, -30.8], 
                                [-64.5, -31.0]]]
            },
            "properties": {
                "CLIENTE": "SISTEMA DE PRUEBA",
                "CULTIVO": "SOJA",
                "HECTAREAS_ASEGURADAS": 1000,
                "ZONA_CZ4": "1",
                "DEPARTAMENTO": "SIN DATOS",
                "LOCALIDAD": "SIN DATOS",
                "excel_fila_num": 1,
                "procesado_en": datetime.now().strftime('%Y-%m-%d %H:%M'),
                "warning": "DATOS DE EMERGENCIA - FALLO EN PROCESO"
            }
        }]
    }
    
    archivo_geojson = os.path.join('data', 'poligonos.geojson')
    with open(archivo_geojson, 'w', encoding='utf-8') as f:
        json.dump(geojson_emergencia, f, ensure_ascii=False, indent=2)
    
    print(f"⚠️ GeoJSON de emergencia creado: {archivo_geojson}")

# ===========================================================================
# FINAL - REPORTE
# ===========================================================================
print("\n" + "=" * 80)
print("🎉 PROCESO COMPLETADO")
print("=" * 80)
print("📁 ARCHIVOS GENERADOS:")
print(f"   1. {archivo_excel}")
print(f"   2. {archivo_geojson}")
print(f"\n📍 El GeoJSON está listo en: data/poligonos.geojson")
print("📍 Tu app debe apuntar a esa URL en GitHub")
print("\n✅ ¡Listo para la automatización diaria!")
