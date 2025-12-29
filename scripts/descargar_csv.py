#!/usr/bin/env python3
"""
DESCARGADOR AUTOMÁTICO DE CSV - Para GitHub Actions
Descarga CSV de multiriesgo-cba.com y lo guarda
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
from webdriver_manager.chrome import ChromeDriverManager

print("=" * 60)
print("🤖 INICIANDO DESCARGA AUTOMÁTICA DE CSV")
print("=" * 60)

# ============================================
# 1. CONFIGURACIÓN (desde variables de entorno)
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
# 2. CONFIGURAR CHROME (modo servidor)
# ============================================
def setup_chrome_for_server():
    """Configurar Chrome para ejecución en servidor"""
    chrome_options = Options()
    
    # Configuración para GitHub Actions
    chrome_options.add_argument('--headless')  # Sin ventana
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Para descargas automáticas
    prefs = {
        "download.default_directory": os.getcwd(),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Ocultar que es automatización
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    return chrome_options

# ============================================
# 3. FUNCIÓN PRINCIPAL DE DESCARGA
# ============================================
def descargar_csv():
    """Función principal que descarga el CSV"""
    print("\n🔧 Configurando ChromeDriver...")
    
    try:
        # Configurar Chrome
        chrome_options = setup_chrome_for_server()
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome configurado")
        
        # ====================================
        # 4. LOGIN EN MULTIRIESGO-CBA
        # ====================================
        print("\n🔐 Accediendo a multiriesgo-cba.com...")
        driver.get("https://multiriesgo-cba.com/user/login/")
        time.sleep(3)
        
        # Ingresar usuario
        usuario_input = driver.find_element(By.NAME, "username")
        usuario_input.send_keys(USUARIO)
        
        # Ingresar contraseña
        contrasena_input = driver.find_element(By.NAME, "password")
        contrasena_input.send_keys(CONTRASENA)
        
        # Hacer clic en login
        boton_login = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        boton_login.click()
        time.sleep(3)
        
        print("✅ Login exitoso")
        
        # ====================================
        # 5. DESCARGAR CSV
        # ====================================
        print("\n📥 Buscando botón 'Descargar CSV'...")
        
        # Esperar a que cargue la página
        time.sleep(2)
        
        # Buscar el botón
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
            driver.quit()
            return False
        
        # Hacer clic en el botón
        print("🖱️  Haciendo clic en el botón...")
        boton_csv.click()
        
        # Esperar la descarga (más tiempo en servidor)
        print("⏳ Esperando descarga (puede tardar 10-20 segundos)...")
        time.sleep(15)
        
        # ====================================
        # 6. VERIFICAR ARCHIVO DESCARGADO
        # ====================================
        print("\n🔍 Buscando archivo CSV descargado...")
        
        archivos = os.listdir('.')
        archivos_csv = [f for f in archivos if f.lower().endswith('.csv')]
        
        if archivos_csv:
            # Ordenar por fecha de modificación (más reciente primero)
            archivos_csv.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            archivo_csv = archivos_csv[0]
            
            tamaño = os.path.getsize(archivo_csv)
            print(f"✅ ARCHIVO DESCARGADO: {archivo_csv}")
            print(f"📏 Tamaño: {tamaño:,} bytes")
            
            # Renombrar a nombre consistente
            nuevo_nombre = "datos_actualizados.csv"
            if archivo_csv != nuevo_nombre:
                os.rename(archivo_csv, nuevo_nombre)
                print(f"📝 Renombrado a: {nuevo_nombre}")
            
            # Mostrar primeras líneas
            try:
                with open(nuevo_nombre, 'r', encoding='utf-8') as f:
                    primera_linea = f.readline().strip()
                    print(f"\n📄 Primera línea del CSV:")
                    print(f"   {primera_linea[:100]}...")
            except:
                pass
            
            resultado = True
            
        else:
            print("❌ No se encontró ningún archivo CSV descargado")
            resultado = False
        
        # ====================================
        # 7. LIMPIAR Y CERRAR
        # ====================================
        print("\n🧹 Cerrando navegador...")
        driver.quit()
        
        return resultado
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE EL PROCESO:")
        print(f"   {type(e).__name__}: {str(e)}")
        
        import traceback
        traceback.print_exc()
        
        return False

# ============================================
# 8. EJECUTAR SI ES EL SCRIPT PRINCIPAL
# ============================================
if __name__ == "__main__":
    print(f"\n📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    exito = descargar_csv()
    
    if exito:
        print("\n" + "=" * 60)
        print("🎉 ¡DESCARGA COMPLETADA EXITOSAMENTE!")
        print("=" * 60)
        sys.exit(0)  # Código de éxito
    else:
        print("\n" + "=" * 60)
        print("❌ LA DESCARGA FALLÓ")
        print("=" * 60)
        sys.exit(1)  # Código de error
