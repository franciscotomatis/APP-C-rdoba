#!/usr/bin/env python3
"""
DESCARGADOR AUTOMÁTICO DE CSV - Versión corregida para GitHub Actions
"""
import os
import sys
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import subprocess

print("=" * 60)
print("🤖 INICIANDO DESCARGA AUTOMÁTICA DE CSV (VERSIÓN CORREGIDA)")
print("=" * 60)

# ============================================
# 1. CONFIGURACIÓN
# ============================================
USUARIO = os.environ.get('MULTIRIESGO_USUARIO', '')
CONTRASENA = os.environ.get('MULTIRIESGO_CONTRASENA', '')

if not USUARIO or not CONTRASENA:
    print("❌ ERROR: Faltan credenciales en variables de entorno")
    print("   Configura MULTIRIESGO_USUARIO y MULTIRIESGO_CONTRASENA")
    sys.exit(1)

print(f"🔐 Usuario configurado: {USUARIO}")
print(f"📂 Directorio actual: {os.getcwd()}")

# ============================================
# 2. INSTALAR CHROMEDRIVER MANUALMENTE
# ============================================
def instalar_chromedriver():
    """Instalar ChromeDriver manualmente para GitHub Actions"""
    print("🔧 Instalando ChromeDriver...")
    
    try:
        # Instalar Chrome y dependencias
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "wget", "unzip", "chromium-browser"], check=True)
        
        # Descargar ChromeDriver específico
        chrome_version = "120.0.6099.109"  # Versión estable
        url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{chrome_version}/linux64/chromedriver-linux64.zip"
        
        print(f"📥 Descargando ChromeDriver {chrome_version}...")
        subprocess.run(["wget", "-q", "-O", "/tmp/chromedriver.zip", url], check=True)
        
        # Extraer
        print("📦 Extrayendo ChromeDriver...")
        subprocess.run(["unzip", "-q", "/tmp/chromedriver.zip", "-d", "/tmp/"], check=True)
        
        # Hacer ejecutable
        chromedriver_path = "/tmp/chromedriver-linux64/chromedriver"
        subprocess.run(["chmod", "+x", chromedriver_path], check=True)
        
        print(f"✅ ChromeDriver instalado en: {chromedriver_path}")
        return chromedriver_path
        
    except Exception as e:
        print(f"❌ Error instalando ChromeDriver: {str(e)}")
        return None

# ============================================
# 3. CONFIGURAR CHROME
# ============================================
def setup_chrome():
    """Configurar Chrome para GitHub Actions"""
    chrome_options = Options()
    
    # Configuración para servidor
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Para evitar detección como bot
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Para descargas
    prefs = {
        "download.default_directory": os.getcwd(),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    return chrome_options

# ============================================
# 4. FUNCIÓN PRINCIPAL DE DESCARGA
# ============================================
def descargar_csv():
    """Descargar CSV de multiriesgo-cba.com"""
    
    driver = None
    
    try:
        # 1. Instalar ChromeDriver
        chromedriver_path = instalar_chromedriver()
        if not chromedriver_path:
            return False
        
        # 2. Configurar Chrome
        chrome_options = setup_chrome()
        service = Service(chromedriver_path)
        
        print("🚀 Iniciando navegador...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Navegador iniciado")
        
        # 3. LOGIN
        print("\n🔐 Accediendo a multiriesgo-cba.com...")
        driver.get("https://multiriesgo-cba.com/user/login/")
        time.sleep(3)
        
        # Ingresar credenciales
        usuario_input = driver.find_element(By.NAME, "username")
        usuario_input.send_keys(USUARIO)
        
        contrasena_input = driver.find_element(By.NAME, "password")
        contrasena_input.send_keys(CONTRASENA)
        
        # Hacer clic en login
        boton_login = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        boton_login.click()
        time.sleep(3)
        
        print("✅ Login exitoso")
        
        # 4. DESCARGAR CSV
        print("\n📥 Buscando botón 'Descargar CSV'...")
        time.sleep(2)
        
        # Buscar botón
        botones = driver.find_elements(By.TAG_NAME, "button")
        boton_csv = None
        
        for boton in botones:
            texto = boton.text.strip()
            if 'descargar csv' in texto.lower():
                boton_csv = boton
                print(f"✅ Botón encontrado: '{texto}'")
                break
        
        if not boton_csv:
            print("❌ No se encontró el botón 'Descargar CSV'")
            return False
        
        # Hacer clic
        print("🖱️  Haciendo clic en el botón...")
        boton_csv.click()
        
        # Esperar descarga
        print("⏳ Esperando descarga (20 segundos)...")
        time.sleep(20)
        
        # 5. VERIFICAR ARCHIVO
        print("\n🔍 Buscando archivo CSV descargado...")
        
        archivos = os.listdir('.')
        archivos_csv = [f for f in archivos if f.lower().endswith('.csv')]
        
        if archivos_csv:
            archivos_csv.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            archivo_csv = archivos_csv[0]
            
            tamaño = os.path.getsize(archivo_csv)
            print(f"✅ ARCHIVO DESCARGADO: {archivo_csv}")
            print(f"📏 Tamaño: {tamaño:,} bytes")
            
            # Renombrar
            nuevo_nombre = "datos_actualizados.csv"
            if archivo_csv != nuevo_nombre:
                os.rename(archivo_csv, nuevo_nombre)
                print(f"📝 Renombrado a: {nuevo_nombre}")
            
            return True
        else:
            print("❌ No se encontró ningún archivo CSV")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        return False
        
    finally:
        if driver:
            print("\n🧹 Cerrando navegador...")
            driver.quit()

# ============================================
# 5. EJECUTAR
# ============================================
if __name__ == "__main__":
    print(f"\n📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    exito = descargar_csv()
    
    if exito:
        print("\n" + "=" * 60)
        print("🎉 ¡DESCARGA COMPLETADA EXITOSAMENTE!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ LA DESCARGA FALLÓ")
        print("=" * 60)
        sys.exit(1)
