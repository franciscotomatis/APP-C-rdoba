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

# --- CONFIGURACIÓN ---
USUARIO = "Ftomatis"
CLAVE = "Sancor2025"

def ejecutar_proceso():
    print("🚀 Iniciando proceso de descarga y conversión...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Configuración de descargas en la carpeta actual
    prefs = {"download.default_directory": os.getcwd()}
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # 1. LOGIN
        print("🔐 Iniciando sesión en Multiriesgo...")
        driver.get("https://www.multiriesgo.com.ar/m-multiriesgo/login.aspx")
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "txtUsuario"))).send_keys(USUARIO)
        driver.find_element(By.ID, "txtPassword").send_keys(CLAVE)
        driver.find_element(By.ID, "btnAceptar").click()
        
        # Esperar que cargue el dashboard
        time.sleep(5)

        # 2. IR AL REPORTE Y DESCARGAR
        print("📥 Navegando al reporte y descargando...")
        driver.get("https://www.multiriesgo.com.ar/m-multiriesgo/Reportes/Consultas_Reporte_Dinamico.aspx?ID_REPORTE=173")
        
        btn_excel = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "btnExportarExcel")))
        btn_excel.click()
        
        # Esperar la descarga (ajustado a 15 segundos)
        time.sleep(15)

        # 3. PROCESAMIENTO DEL ARCHIVO
        archivos = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.csv')]
        
        if not archivos:
            print("❌ Error: No se encontró el archivo descargado.")
            return

        archivo_descargado = archivos[0]
        print(f"📦 Procesando archivo: {archivo_descargado}")

        # Leer Excel o CSV
        if archivo_descargado.endswith('.xlsx'):
            df = pd.read_excel(archivo_descargado)
        else:
            df = pd.read_csv(archivo_descargado)

        # 4. CONVERSIÓN A GEOJSON (SIN MAPA)
        print("🗺️ Convirtiendo coordenadas a GeoJSON...")
        if 'POLIGONO' in df.columns:
            df['geometry'] = df['POLIGONO'].apply(wkt.loads)
            gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
            
            # Guardar el archivo final
            gdf.to_file("poligonos.geojson", driver='GeoJSON')
            print("✅ Archivo 'poligonos.geojson' creado exitosamente.")
        else:
            print("❌ Error: No se encontró la columna 'POLIGONO' en el reporte.")

    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    ejecutar_proceso()
