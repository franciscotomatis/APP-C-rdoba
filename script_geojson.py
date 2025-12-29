import os
import time
import pandas as pd
import geopandas as gpd
from shapely import wkt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURACIÓN DESDE SECRETS DE GITHUB ---
# Estos nombres deben coincidir con los que pusiste en el .yml
USUARIO = os.getenv('MULTIRIESGO_USUARIO')
CLAVE = os.getenv('MULTIRIESGO_CONTRASENA')

def ejecutar_proceso():
    print("🚀 Iniciando proceso de descarga y conversión en GitHub Actions...")
    
    if not USUARIO or not CLAVE:
        print("❌ Error: No se encontraron las credenciales en los Secrets.")
        return

    chrome_options = Options()
    chrome_options.add_argument("--headless") # Obligatorio para GitHub
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Carpeta de descarga: la raíz del repo en GitHub
    prefs = {"download.default_directory": os.getcwd()}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # 1. LOGIN
        print("🔐 Iniciando sesión en Multiriesgo...")
        driver.get("https://www.multiriesgo.com.ar/m-multiriesgo/login.aspx")
        
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "txtUsuario"))).send_keys(USUARIO)
        driver.find_element(By.ID, "txtPassword").send_keys(CLAVE)
        driver.find_element(By.ID, "btnAceptar").click()
        
        time.sleep(5)

        # 2. IR AL REPORTE Y DESCARGAR
        print("📥 Navegando al reporte 173...")
        driver.get("https://www.multiriesgo.com.ar/m-multiriesgo/Reportes/Consultas_Reporte_Dinamico.aspx?ID_REPORTE=173")
        
        btn_excel = WebDriverWait(driver, 25).until(EC.element_to_be_clickable((By.ID, "btnExportarExcel")))
        btn_excel.click()
        
        print("⏳ Esperando descarga del archivo...")
        time.sleep(20) # Aumentamos tiempo por si el servidor de Multiriesgo está lento

        # 3. IDENTIFICAR EL ARCHIVO DESCARGADO
        archivos = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.csv')]
        
        if not archivos:
            print("❌ Error: El archivo no se descargó o tardó demasiado.")
            return

        archivo_descargado = archivos[0]
        print(f"📦 Archivo detectado: {archivo_descargado}")

        # Leer Excel o CSV
        if archivo_descargado.endswith('.xlsx'):
            df = pd.read_excel(archivo_descargado)
        else:
            df = pd.read_csv(archivo_descargado)

        # 4. CONVERSIÓN A GEOJSON
        print("🗺️ Procesando columna POLIGONO a GeoJSON...")
        if 'POLIGONO' in df.columns:
            # Limpiar WKT si fuera necesario y convertir
            df['geometry'] = df['POLIGONO'].apply(wkt.loads)
            gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
            
            # Guardar el archivo que leerá generar_visor.py
            gdf.to_file("poligonos.geojson", driver='GeoJSON')
            print("✅ Archivo 'poligonos.geojson' listo para la App.")
        else:
            print(f"❌ Error: No se encontró la columna 'POLIGONO'. Columnas encontradas: {df.columns.tolist()}")

    except Exception as e:
        print(f"❌ Ocurrió un error durante el proceso: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    ejecutar_proceso()
