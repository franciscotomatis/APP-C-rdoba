#!/usr/bin/env python3
"""
Descarga automática de CSV desde multiriesgo-cba.com
Versión optimizada para GitHub Actions
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
from selenium.webdriver.common.keys import Keys
import pandas as pd

def setup_chrome_for_github():
    """Configurar Chrome específicamente para GitHub Actions"""
    print("🔧 Configurando Chrome para GitHub Actions...")
    
    chrome_options = Options()
    
    # CONFIGURACIÓN CRÍTICA PARA GITHUB ACTIONS
    chrome_options.add_argument('--headless=new')  # IMPORTANTE: 'new' para Chrome 109+
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Deshabilitar sandbox adicional (necesario en CI/CD)
    chrome_options.add_argument('--disable-setuid-sandbox')
    
    # Ocultar que somos un bot
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Configurar descargas
    download_dir = os.path.join(os.getcwd(), 'data')
    os.makedirs(download_dir, exist_ok=True)
    print(f"📂 Directorio de descargas: {download_dir}")
    
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "safebrowsing.enabled": False,  # Deshabilitar para evitar bloqueos
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    })
    
    return chrome_options

def wait_for_download_complete(download_dir, timeout=60):
    """Esperar a que se complete una descarga"""
    print(f"⏳ Esperando descarga en {download_dir}...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Listar archivos en el directorio
        if os.path.exists(download_dir):
            files = os.listdir(download_dir)
            
            # Buscar archivos CSV
            csv_files = [f for f in files if f.lower().endswith('.csv')]
            
            if csv_files:
                # Tomar el más reciente
                csv_files.sort(key=lambda x: os.path.getctime(os.path.join(download_dir, x)), reverse=True)
                latest_file = csv_files[0]
                file_path = os.path.join(download_dir, latest_file)
                
                # Verificar que el archivo no esté siendo escrito
                initial_size = os.path.getsize(file_path)
                time.sleep(2)
                final_size = os.path.getsize(file_path)
                
                if initial_size == final_size and initial_size > 100:  # Al menos 100 bytes
                    print(f"✅ Descarga completada: {latest_file} ({final_size:,} bytes)")
                    return file_path
                else:
                    print(f"⏳ Archivo aún descargando: {latest_file} ({initial_size} -> {final_size} bytes)")
        
        time.sleep(1)
    
    print("❌ Timeout esperando descarga")
    return None

def perform_login(driver, username, password):
    """Realizar login en el sitio"""
    print("🔐 Realizando login...")
    
    try:
        # Ir a la página de login
        login_url = "https://multiriesgo-cba.com/user/login/"
        driver.get(login_url)
        time.sleep(3)
        
        print(f"📍 Página actual: {driver.current_url}")
        print(f"📄 Título: {driver.title}")
        
        # Tomar screenshot para debug (solo si no es headless)
        try:
            driver.save_screenshot('login_page.png')
            print("📸 Screenshot guardado: login_page.png")
        except:
            pass
        
        # Buscar campos de login
        print("🔍 Buscando campos de login...")
        
        # Estrategia 1: Buscar por name
        try:
            username_field = driver.find_element(By.NAME, "username")
            password_field = driver.find_element(By.NAME, "password")
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            
            print("✅ Campos encontrados por NAME")
            
        except:
            # Estrategia 2: Buscar por cualquier input
            print("⚠️ No se encontraron por NAME, buscando alternativas...")
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            print(f"📋 Inputs encontrados: {len(all_inputs)}")
            
            for i, inp in enumerate(all_inputs):
                input_type = inp.get_attribute("type")
                input_name = inp.get_attribute("name")
                input_id = inp.get_attribute("id")
                print(f"  Input {i}: type={input_type}, name={input_name}, id={input_id}")
            
            # Intentar con los primeros inputs que parezcan login
            if len(all_inputs) >= 2:
                username_field = all_inputs[0]
                password_field = all_inputs[1]
                login_button = driver.find_element(By.TAG_NAME, "button")
            else:
                raise Exception("No se encontraron suficientes campos de login")
        
        # Ingresar credenciales
        print("⌨️ Ingresando credenciales...")
        username_field.clear()
        username_field.send_keys(username)
        
        password_field.clear()
        password_field.send_keys(password)
        
        # Hacer login
        print("🖱️ Haciendo clic en login...")
        login_button.click()
        time.sleep(5)
        
        # Verificar login exitoso
        print(f"📍 URL después de login: {driver.current_url}")
        print(f"📄 Título después de login: {driver.title}")
        
        # Verificar que estamos en dashboard o página principal
        if "login" not in driver.current_url.lower():
            print("✅ Login aparentemente exitoso")
            return True
        else:
            print("❌ Posible falla en login - aún en página de login")
            return False
            
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def find_csv_download_button(driver):
    """Buscar y hacer clic en el botón de descarga CSV"""
    print("🔍 Buscando botón de descarga CSV...")
    
    strategies = [
        # Estrategia 1: Buscar por texto
        lambda: find_by_text(driver, ['descargar csv', 'exportar csv', 'csv', 'download csv']),
        
        # Estrategia 2: Buscar por atributos
        lambda: find_by_attributes(driver),
        
        # Estrategia 3: Buscar enlaces CSV
        lambda: find_csv_links(driver),
        
        # Estrategia 4: Buscar formularios de exportación
        lambda: find_export_forms(driver)
    ]
    
    for i, strategy in enumerate(strategies):
        print(f"\n🎯 Probando estrategia {i+1}...")
        result = strategy()
        if result:
            return result
    
    return None

def find_by_text(driver, keywords):
    """Buscar elementos por texto"""
    try:
        # Buscar en botones
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            button_text = button.text.lower()
            for keyword in keywords:
                if keyword in button_text:
                    print(f"✅ Botón encontrado: '{button.text}'")
                    return button
        
        # Buscar en enlaces
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            link_text = link.text.lower()
            link_href = link.get_attribute('href') or ''
            for keyword in keywords:
                if keyword in link_text or '.csv' in link_href.lower():
                    print(f"✅ Enlace encontrado: '{link.text}' -> {link_href[:50]}...")
                    return link
        
        # Buscar en inputs
        inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='submit'], input[type='button']")
        for inp in inputs:
            value = inp.get_attribute('value') or ''
            if any(keyword in value.lower() for keyword in keywords):
                print(f"✅ Input encontrado: '{value}'")
                return inp
                
    except Exception as e:
        print(f"⚠️ Error en búsqueda por texto: {str(e)[:50]}")
    
    return None

def find_by_attributes(driver):
    """Buscar por atributos específicos"""
    try:
        # Buscar elementos con data-csv, data-export, etc.
        selectors = [
            "[data-csv]", "[data-export]", "[data-download]",
            "[onclick*='csv']", "[onclick*='export']", "[onclick*='download']"
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Elemento encontrado por selector: {selector}")
                    return elements[0]
            except:
                pass
                
    except Exception as e:
        print(f"⚠️ Error en búsqueda por atributos: {str(e)[:50]}")
    
    return None

def find_csv_links(driver):
    """Buscar enlaces directos a CSV"""
    try:
        links = driver.find_elements(By.TAG_NAME, "a")
        csv_links = []
        
        for link in links:
            href = link.get_attribute('href') or ''
            if '.csv' in href.lower():
                csv_links.append((link, href))
        
        if csv_links:
            print(f"✅ Encontrados {len(csv_links)} enlaces CSV")
            return csv_links[0][0]  # Devolver el primer enlace
            
    except Exception as e:
        print(f"⚠️ Error buscando enlaces CSV: {str(e)[:50]}")
    
    return None

def find_export_forms(driver):
    """Buscar formularios de exportación"""
    try:
        forms = driver.find_elements(By.TAG_NAME, "form")
        
        for form in forms:
            action = form.get_attribute('action') or ''
            if 'export' in action.lower() or 'csv' in action.lower():
                print(f"✅ Formulario de exportación encontrado: {action[:50]}...")
                return form
                
    except Exception as e:
        print(f"⚠️ Error buscando formularios: {str(e)[:50]}")
    
    return None

def download_csv():
    """Función principal de descarga"""
    print("=" * 60)
    print("🚀 INICIANDO DESCARGA AUTOMÁTICA DE CSV")
    print("=" * 60)
    
    # Obtener credenciales de variables de entorno
    username = os.environ.get('MULTIRIESGO_USER', 'Sancor')
    password = os.environ.get('MULTIRIESGO_PASS', '2025Sancor')
    
    print(f"🔐 Usuario configurado: {username}")
    print(f"🔐 Password configurado: {'*' * len(password) if password else 'NO CONFIGURADO'}")
    
    if not username or not password:
        print("❌ ERROR: Credenciales no configuradas")
        print("   Configura los Secrets en GitHub:")
        print("   - MULTIRIESGO_USER")
        print("   - MULTIRIESGO_PASS")
        return False
    
    driver = None
    try:
        # 1. Configurar Chrome
        chrome_options = setup_chrome_for_github()
        
        # 2. Inicializar driver con webdriver-manager
        print("🚗 Inicializando ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 3. Realizar login
        login_success = perform_login(driver, username, password)
        if not login_success:
            print("❌ Falló el login, abortando...")
            return False
        
        # 4. Esperar a que cargue el dashboard
        print("⏳ Esperando carga del dashboard...")
        time.sleep(5)
        
        # Tomar screenshot del dashboard
        try:
            driver.save_screenshot('dashboard.png')
            print("📸 Screenshot del dashboard: dashboard.png")
        except:
            pass
        
        # 5. Buscar botón de descarga
        print("\n🔍 Navegando para encontrar CSV...")
        download_button = find_csv_download_button(driver)
        
        if not download_button:
            print("❌ No se encontró botón de descarga CSV")
            
            # Intentar navegar a posibles URLs de exportación
            export_urls = [
                "https://multiriesgo-cba.com/export/csv/",
                "https://multiriesgo-cba.com/dashboard/export/",
                "https://multiriesgo-cba.com/reports/export/csv/"
            ]
            
            for url in export_urls:
                print(f"🔗 Intentando URL directa: {url}")
                try:
                    driver.get(url)
                    time.sleep(3)
                    
                    # Verificar si se descargó algo
                    download_dir = os.path.join(os.getcwd(), 'data')
                    csv_file = wait_for_download_complete(download_dir, timeout=10)
                    if csv_file:
                        print(f"✅ Descarga exitosa desde URL directa: {csv_file}")
                        return True
                except:
                    continue
            
            return False
        
        # 6. Hacer clic en el botón
        print("🖱️ Haciendo clic en el botón de descarga...")
        try:
            driver.execute_script("arguments[0].click();", download_button)
        except:
            download_button.click()
        
        # 7. Esperar descarga
        download_dir = os.path.join(os.getcwd(), 'data')
        csv_file = wait_for_download_complete(download_dir, timeout=30)
        
        if csv_file:
            print(f"\n🎉 ¡ÉXITO! CSV descargado: {csv_file}")
            
            # Opcional: Convertir a XLSX
            try:
                print("🔄 Convirtiendo CSV a XLSX...")
                df = pd.read_csv(csv_file)
                xlsx_file = os.path.join(download_dir, 'latest.xlsx')
                df.to_excel(xlsx_file, index=False)
                print(f"✅ Convertido a XLSX: {xlsx_file}")
            except Exception as e:
                print(f"⚠️ No se pudo convertir a XLSX: {str(e)[:50]}")
            
            return True
        else:
            print("❌ No se pudo descargar el CSV")
            return False
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if driver:
            print("\n🔒 Cerrando navegador...")
            driver.quit()

def main():
    """Función principal"""
    success = download_csv()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ PROCESO FALLÓ")
        print("=" * 60)
        exit(1)

if __name__ == "__main__":
    main()
