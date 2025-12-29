import os, time, json, pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Buscamos los secretos con los nombres que creaste
USUARIO = os.environ.get('MULTIRIESGO_USUARIO')
CONTRASENA = os.environ.get('MULTIRIESGO_CONTRASENA')

def convertir_a_geojson(archivo_csv):
    print("🛠️ Iniciando conversión a GeoJSON...")
    df = pd.read_csv(archivo_csv)
    df.columns = df.columns.str.replace('﻿', '').str.strip()
    
    features = []
    for i, row in df.iterrows():
        geo_data = row['GEOJSON']
        if pd.isna(geo_data): continue
        try:
            geometria = json.loads(geo_data)
            propiedades = row.drop('GEOJSON').to_dict()
            features.append({
                "type": "Feature",
                "properties": propiedades,
                "geometry": geometria
            })
        except: continue
    
    # Nombre fijo para que tu App siempre encuentre el mismo archivo
    nombre_final = "poligonos.geojson"
    with open(nombre_final, 'w', encoding='utf-8') as f:
        json.dump({"type": "FeatureCollection", "features": features}, f, ensure_ascii=False)
    
    print(f"✅ Archivo {nombre_final} generado con éxito.")

def ejecutar():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option("prefs", {"download.default_directory": os.getcwd()})

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print("🔐 Entrando a la web...")
        driver.get("https://multiriesgo-cba.com/user/login/")
        time.sleep(4)
        driver.find_element(By.NAME, "username").send_keys(USUARIO)
        driver.find_element(By.NAME, "password").send_keys(CONTRASENA)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(6)

        print("📥 Buscando descarga...")
        botones = driver.find_elements(By.TAG_NAME, 'button')
        boton_csv = next((b for b in botones if 'descargar csv' in b.text.lower()), None)
        
        if boton_csv:
            driver.execute_script("arguments[0].click();", boton_csv)
            time.sleep(15) 
            
            archivos = [f for f in os.listdir('.') if f.endswith('.csv')]
            if archivos:
                csv_descargado = max(archivos, key=os.path.getctime)
                convertir_a_geojson(csv_descargado)
                os.remove(csv_descargado) 
            else:
                print("❌ No se encontró el CSV descargado.")
    finally:
        driver.quit()

if __name__ == "__main__":
    ejecutar()
