#!/usr/bin/env python3
"""
Descarga automática de CSV desde multiriesgo-cba.com
Para ejecutar en GitHub Actions
"""

import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def setup_chrome():
    """Configurar Chrome para GitHub Actions"""
    print("🔧 Configurando Chrome...")
    
    chrome_options = Options()
    
    # Para GitHub Actions (headless)
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Configurar descargas
    download_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(download_dir, exist_ok=True)
    
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    })
    
    return chrome_options

def wait_for_download(download_dir, timeout=60):
    """Esperar a que se complete la descarga"""
    print("⏳ Esperando descarga...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        files = os.listdir(download_dir)
        csv_files = [f for f in files if f.lower().endswith('.csv')]
        
        if csv_files:
            # Tomar el más reciente
            csv_files.sort(key=lambda x: os.path.getctime(os.path.join(download_dir, x)), reverse=True)
            latest_file = csv_files[0]
            file_path = os.path.join(download_dir, latest_file)
            
            # Verificar que no esté siendo escrito
            time.sleep(2)
            return file_path
        
        time.sleep(1)
    
    return None

def download_csv():
    """Función principal de descarga"""
    print("🚀 Iniciando descarga automática")
    
    # Obtener credenciales de variables de entorno
    username = os.environ.get('MULTIRIESGO_USER', 'Sancor')
    password = os.environ.get('MULTIRIESGO_PASS', '2025Sancor')
    
    if not username or not password:
        print("❌ Credenciales no configuradas")
        return False
    
    driver = None
    try:
        # Configurar Chrome
        chrome_options = setup_chrome()
        download_dir = os.path.join(os.getcwd(), 'data')
        
        # Instalar driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 1. Login
        print("🔐 Iniciando sesión...")
        driver.get("https://multiriesgo-cba.com/user/login/")
        time.sleep(3)
        
        # Encontrar campos de login
        try:
            wait = WebDriverWait(driver, 10)
            user_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
            pass_input = driver.find_element(By.NAME, "password")
            login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            user_input.send_keys(username)
            pass_input.send_keys(password)
            login_btn.click()
            print("✅ Login exitoso")
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Error en login: {str(e)}")
            return False
        
        # 2. Verificar dashboard
        if "dashboard" not in driver.current_url:
            print("⚠️ Posible fallo en login, continuando...")
        
        # 3. Buscar y descargar CSV
        print("📥 Buscando opción de descarga...")
        
        # Intentar diferentes estrategias
        strategies = [
            # Estrategia 1: Buscar enlace directo
            lambda: find_and_click_csv_link(driver),
            # Estrategia 2: Buscar botón
            lambda: find_and_click_csv_button(driver),
            # Estrategia 3: Buscar formulario
            lambda: find_and_submit_csv_form(driver)
        ]
        
        csv_path = None
        for i, strategy in enumerate(strategies):
            print(f"\n🎯 Probando estrategia {i+1}...")
            csv_path = strategy()
            if csv_path:
                break
        
        if csv_path:
            print(f"✅ CSV descargado: {csv_path}")
            
            # Convertir a XLSX (opcional)
            try:
                df = pd.read_csv(csv_path)
                xlsx_path = os.path.join(download_dir, 'latest.xlsx')
                df.to_excel(xlsx_path, index=False)
                print(f"✅ Convertido a XLSX: {xlsx_path}")
            except Exception as e:
                print(f"⚠️ No se pudo convertir a XLSX: {str(e)}")
            
            return True
        else:
            print("❌ No se pudo descargar el CSV")
            return False
            
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if driver:
            driver.quit()
            print("🔒 Navegador cerrado")

def find_and_click_csv_link(driver):
    """Buscar enlaces CSV"""
    try:
        links = driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            href = link.get_attribute('href') or ''
            text = link.text.lower()
            
            if '.csv' in href.lower() or 'csv' in text:
                print(f"🔗 Enlace CSV encontrado: {text[:50]}")
                driver.execute_script("arguments[0].click();", link)
                time.sleep(5)
                
                csv_path = wait_for_download(os.path.join(os.getcwd(), 'data'))
                if csv_path:
                    return csv_path
    except:
        pass
    return None

def find_and_click_csv_button(driver):
    """Buscar botones CSV"""
    try:
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        for button in buttons:
            text = button.text.lower()
            if 'descargar csv' in text or 'exportar csv' in text:
                print(f"🖱️ Botón CSV encontrado: {text[:50]}")
                driver.execute_script("arguments[0].click();", button)
                time.sleep(5)
                
                csv_path = wait_for_download(os.path.join(os.getcwd(), 'data'))
                if csv_path:
                    return csv_path
    except:
        pass
    return None

def find_and_submit_csv_form(driver):
    """Buscar formularios CSV"""
    try:
        forms = driver.find_elements(By.TAG_NAME, 'form')
        for form in forms:
            action = form.get_attribute('action') or ''
            if 'export' in action.lower() or 'csv' in action.lower():
                print(f"📋 Formulario CSV encontrado")
                form.submit()
                time.sleep(5)
                
                csv_path = wait_for_download(os.path.join(os.getcwd(), 'data'))
                if csv_path:
                    return csv_path
    except:
        pass
    return None

if __name__ == "__main__":
    success = download_csv()
    if success:
        print("🎉 Proceso de descarga completado exitosamente")
        exit(0)
    else:
        print("❌ Proceso de descarga falló")
        exit(1)
