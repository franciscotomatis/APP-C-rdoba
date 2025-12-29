#!/usr/bin/env python3
"""
DESCARGADOR AUTOMÁTICO DE CSV - VERSIÓN CORREGIDA PARA GITHUB ACTIONS 143.0.7499.109
"""
import os
import sys
import time
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import subprocess
import requests

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
# 2. INSTALAR CHROMEDRIVER DINÁMICAMENTE
# ============================================
def instalar_chromedriver():
    """Instalar ChromeDriver que sea compatible con Chrome 143.0.7499.109"""
    print("🔧 Instalando ChromeDriver para Chrome 143...")
    
    try:
        # PRIMERO: Intentar con webdriver-manager (lo maneja automáticamente)
        print("📥 Probando webdriver-manager...")
        from webdriver_manager.chrome import ChromeDriverManager
        chromedriver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver instalado con webdriver-manager: {chromedriver_path}")
        return chromedriver_path
        
    except Exception as e:
        print(f"⚠️  Error con webdriver-manager: {str(e)[:100]}")
        print("🔄 Usando método manual específico para Chrome 143...")
        
        try:
            # SEGUNDO: Método manual - Descargar versión EXACTA para Chrome 143
            chrome_version = "143.0.7499.109"  # VERSIÓN EXACTA DEL ERROR
            
            # URL del ChromeDriver compatible
            driver_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{chrome_version}/linux64/chromedriver-linux64.zip"
            
            print(f"📥 Descargando ChromeDriver {chrome_version}...")
            subprocess.run(["wget", "-q", "-O", "/tmp/chromedriver.zip", driver_url], check=True)
            
            print("📦 Extrayendo ChromeDriver...")
            subprocess.run(["unzip", "-q", "/tmp/chromedriver.zip", "-d", "/tmp/"], check=True)
            
            # Verificar si la estructura es diferente
            chromedriver_path = "/tmp/chromedriver-linux64/chromedriver"
            
            # Hacer ejecutable
            subprocess.run(["chmod", "+x", chromedriver_path], check=True)
            
            print(f"✅ ChromeDriver instalado manualmente en: {chromedriver_path}")
            return chromedriver_path
            
        except Exception as e2:
            print(f"❌ Error en método manual: {str(e2)}")
            
            # TERCERO: Intentar con la API de Chrome for Testing
            print("🔄 Intentando con API de Chrome for Testing...")
            try:
                api_url = "https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone.json"
                response = requests.get(api_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Buscar la versión 143
                    if "143" in data:
                        version_info = data["143"]
                        latest_version = version_info["version"]
                        
                        print(f"✅ Encontrada versión 143: {latest_version}")
                        
                        # Descargar
                        driver_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{latest_version}/linux64/chromedriver-linux64.zip"
                        
                        subprocess.run(["wget", "-q", "-O", "/tmp/chromedriver2.zip", driver_url], check=True)
                        subprocess.run(["unzip", "-q", "/tmp/chromedriver2.zip", "-d", "/tmp/"], check=True)
                        
                        # Buscar chromedriver en el extracto
                        chromedriver_candidates = []
                        for root, dirs, files in os.walk("/tmp/"):
                            for file in files:
                                if "chromedriver" in file and not file.endswith('.zip'):
                                    chromedriver_candidates.append(os.path.join(root, file))
                        
                        if chromedriver_candidates:
                            chromedriver_path = chromedriver_candidates[0]
                            subprocess.run(["chmod", "+x", chromedriver_path], check=True)
                            print(f"✅ ChromeDriver encontrado en: {chromedriver_path}")
                            return chromedriver_path
                            
            except Exception as e3:
                print(f"❌ Error con API: {str(e3)}")
            
            print("⚠️  Todos los métodos fallaron, intentando chromedriver existente...")
            
            # ÚLTIMO INTENTO: Verificar si hay chromedriver en PATH
            try:
                result = subprocess.run(["which", "chromedriver"], capture_output=True, text=True)
                if result.returncode == 0:
                    chromedriver_path = result.stdout.strip()
                    print(f"✅ ChromeDriver encontrado en PATH: {chromedriver_path}")
                    return chromedriver_path
            except:
                pass
            
            return None

# ============================================
# 3. CONFIGURAR CHROME PARA GITHUB ACTIONS
# ============================================
def setup_chrome():
    """Configurar Chrome para GitHub Actions"""
    chrome_options = Options()
    
    # Configuración para servidor sin GUI
    chrome_options.add_argument('--headless=new')  # Nueva sintaxis headless
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    # Evitar detección como bot
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Configuración de descargas
    prefs = {
        "download.default_directory": os.getcwd(),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Agregar argumentos adicionales para estabilidad
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-background-networking')
    
    return chrome_options

# ============================================
# 4. FUNCIÓN PRINCIPAL DE DESCARGA
# ============================================
def descargar_csv():
    """Descargar CSV de multiriesgo-cba.com"""
    
    driver = None
    
    try:
        # 1. Instalar ChromeDriver
        print("\n" + "=" * 40)
        print("🔧 CONFIGURANDO CHROMEDRIVER")
        print("=" * 40)
        
        chromedriver_path = instalar_chromedriver()
        if not chromedriver_path:
            print("❌ No se pudo instalar ChromeDriver")
            return False
        
        # 2. Configurar Chrome
        chrome_options = setup_chrome()
        service = Service(chromedriver_path)
        
        print("🚀 Iniciando navegador...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Ejecutar script para evitar detección
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Navegador iniciado exitosamente")
        
        # 3. LOGIN
        print("\n" + "=" * 40)
        print("🔐 INICIANDO SESIÓN")
        print("=" * 40)
        
        print("🌐 Navegando a multiriesgo-cba.com...")
        driver.get("https://multiriesgo-cba.com/user/login/")
        time.sleep(4)  # Esperar carga
        
        print("📝 Ingresando credenciales...")
        
        # Buscar campos de login (probando diferentes selectores)
        usuario_input = None
        contrasena_input = None
        
        # Intentar diferentes selectores para el campo usuario
        selectores_usuario = [
            "input[name='username']",
            "input[name='user']",
            "input[type='text']",
            "#username",
            ".username-input",
            "input#username"
        ]
        
        for selector in selectores_usuario:
            try:
                usuario_input = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Campo usuario encontrado con selector: {selector}")
                break
            except:
                continue
        
        if not usuario_input:
            # Tomar captura de página para debugging
            page_source = driver.page_source[:2000]
            print(f"⚠️  No se encontró campo usuario. HTML inicial: {page_source[:500]}...")
            
            # Intentar encontrar por XPath genérico
            try:
                inputs = driver.find_elements(By.TAG_NAME, "input")
                print(f"📋 Inputs encontrados en página: {len(inputs)}")
                for i, inp in enumerate(inputs):
                    print(f"  Input {i}: type={inp.get_attribute('type')}, name={inp.get_attribute('name')}, id={inp.get_attribute('id')}")
                    
                    if inp.get_attribute('type') in ['text', 'email']:
                        usuario_input = inp
                        print("✅ Campo usuario encontrado por atributo type")
                        break
            except:
                pass
        
        if not usuario_input:
            print("❌ No se pudo encontrar el campo de usuario")
            return False
        
        # Ingresar usuario
        usuario_input.clear()
        usuario_input.send_keys(USUARIO)
        print(f"✅ Usuario ingresado: {USUARIO}")
        
        # Buscar campo contraseña
        selectores_contrasena = [
            "input[name='password']",
            "input[type='password']",
            "#password",
            ".password-input",
            "input#password"
        ]
        
        for selector in selectores_contrasena:
            try:
                contrasena_input = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Campo contraseña encontrado con selector: {selector}")
                break
            except:
                continue
        
        if not contrasena_input:
            # Buscar por atributo type=password
            try:
                contrasena_input = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            except:
                print("❌ No se pudo encontrar el campo de contraseña")
                return False
        
        # Ingresar contraseña
        contrasena_input.clear()
        contrasena_input.send_keys(CONTRASENA)
        print("✅ Contraseña ingresada")
        
        # Buscar y hacer clic en botón de login
        print("🔍 Buscando botón de login...")
        boton_login = None
        
        selectores_boton = [
            "button[type='submit']",
            "input[type='submit']",
            ".login-button",
            "button:contains('Iniciar')",
            "button:contains('Login')",
            "button:contains('Entrar')",
            "input[value='Iniciar sesión']"
        ]
        
        for selector in selectores_boton:
            try:
                if 'contains' in selector:
                    # Buscar por texto (requiere XPath)
                    texto = selector.split("'")[1]
                    boton_login = driver.find_element(By.XPATH, f"//button[contains(text(), '{texto}')]")
                else:
                    boton_login = driver.find_element(By.CSS_SELECTOR, selector)
                
                print(f"✅ Botón login encontrado con selector: {selector}")
                break
            except:
                continue
        
        if not boton_login:
            print("⚠️  Botón no encontrado con selectores CSS, intentando con XPath...")
            try:
                boton_login = driver.find_element(By.XPATH, "//button[contains(., 'Iniciar') or contains(., 'Login') or contains(., 'Entrar')]")
            except:
                try:
                    # Último intento: cualquier botón o input submit
                    botones = driver.find_elements(By.TAG_NAME, "button")
                    inputs = driver.find_elements(By.TAG_NAME, "input")
                    
                    for elem in botones + inputs:
                        if elem.get_attribute('type') == 'submit':
                            boton_login = elem
                            break
                        
                        texto = elem.text.lower()
                        if 'iniciar' in texto or 'login' in texto or 'entrar' in texto:
                            boton_login = elem
                            break
                except:
                    pass
        
        if not boton_login:
            print("❌ No se pudo encontrar el botón de login")
            return False
        
        print("🖱️  Haciendo clic en botón de login...")
        boton_login.click()
        time.sleep(5)  # Esperar redirección
        
        # Verificar si el login fue exitoso
        current_url = driver.current_url
        print(f"🌐 URL actual después de login: {current_url}")
        
        if 'login' in current_url.lower():
            print("⚠️  Posible fallo en login, revisando página...")
            page_content = driver.page_source.lower()
            if 'error' in page_content or 'incorrect' in page_content:
                print("❌ Credenciales incorrectas o error en login")
                return False
        
        print("✅ Login exitoso (asumiendo)")
        
        # 4. BUSCAR Y DESCARGAR CSV
        print("\n" + "=" * 40)
        print("📥 BUSCANDO CSV PARA DESCARGAR")
        print("=" * 40)
        
        print("🔍 Buscando enlaces o botones de descarga...")
        time.sleep(3)
        
        # Buscar cualquier enlace o botón que contenga "CSV" o "Descargar"
        elementos_csv = []
        
        # Buscar enlaces
        enlaces = driver.find_elements(By.TAG_NAME, "a")
        for enlace in enlaces:
            texto = enlace.text.lower()
            href = enlace.get_attribute('href') or ''
            
            if 'csv' in texto or 'descargar' in texto or '.csv' in href:
                elementos_csv.append(('enlace', enlace, texto, href))
                print(f"📎 Enlace CSV encontrado: '{texto[:50]}...' -> {href[:50]}...")
        
        # Buscar botones
        botones = driver.find_elements(By.TAG_NAME, "button")
        for boton in botones:
            texto = boton.text.lower()
            if 'csv' in texto or 'descargar' in texto or 'export' in texto:
                elementos_csv.append(('boton', boton, texto, ''))
                print(f"🔘 Botón CSV encontrado: '{texto[:50]}...'")
        
        # Buscar inputs
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for inp in inputs:
            valor = inp.get_attribute('value') or ''
            if 'csv' in valor.lower() or 'descargar' in valor.lower():
                elementos_csv.append(('input', inp, valor, ''))
                print(f"⌨️  Input CSV encontrado: '{valor[:50]}...'")
        
        if not elementos_csv:
            print("❌ No se encontraron elementos CSV/Descargar en la página")
            print("📋 Tomando captura del HTML para debugging...")
            with open('pagina_despues_login.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("💾 HTML guardado como 'pagina_despues_login.html'")
            return False
        
        print(f"✅ Se encontraron {len(elementos_csv)} elementos potenciales")
        
        # Intentar con cada elemento encontrado
        for i, (tipo, elemento, texto, href) in enumerate(elementos_csv[:3]):  # Probar solo primeros 3
            print(f"\n🔧 Probando elemento {i+1} ({tipo}): '{texto[:30]}...'")
            
            try:
                if tipo == 'enlace' and href:
                    print(f"🌐 Navegando a enlace CSV: {href[:80]}...")
                    driver.get(href)
                else:
                    print("🖱️  Haciendo clic en elemento...")
                    elemento.click()
                
                # Esperar descarga
                print("⏳ Esperando descarga (15 segundos)...")
                time.sleep(15)
                
                # Verificar si se descargó algún archivo
                archivos = os.listdir('.')
                archivos_csv = [f for f in archivos if f.lower().endswith('.csv')]
                
                if archivos_csv:
                    archivos_csv.sort(key=lambda x: os.path.getmtime(x), reverse=True)
                    archivo_csv = archivos_csv[0]
                    
                    tamaño = os.path.getsize(archivo_csv)
                    print(f"✅ ¡ARCHIVO DESCARGADO! {archivo_csv} ({tamaño:,} bytes)")
                    
                    # Renombrar a nombre estándar
                    nuevo_nombre = "datos_actualizados.csv"
                    if archivo_csv != nuevo_nombre:
                        os.rename(archivo_csv, nuevo_nombre)
                        print(f"📝 Renombrado a: {nuevo_nombre}")
                    
                    return True
                else:
                    print(f"⚠️  No se descargó archivo CSV con elemento {i+1}")
                    
            except Exception as e:
                print(f"⚠️  Error con elemento {i+1}: {str(e)[:100]}")
                # Continuar con el siguiente elemento
        
        print("❌ Ninguno de los elementos funcionó para descargar CSV")
        return False
            
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if driver:
            print("\n🧹 Cerrando navegador...")
            try:
                driver.quit()
            except:
                pass

# ============================================
# 5. FUNCIÓN PRINCIPAL
# ============================================
def main():
    print(f"\n📅 Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar que estamos en GitHub Actions
    if 'GITHUB_ACTIONS' in os.environ:
        print("🏗️  Ejecutando en GitHub Actions")
    
    # Ejecutar descarga
    exito = descargar_csv()
    
    if exito:
        print("\n" + "=" * 60)
        print("🎉 ¡DESCARGA COMPLETADA EXITOSAMENTE!")
        print("=" * 60)
        
        # Listar archivos descargados
        print("\n📁 ARCHIVOS DESCARGADOS:")
        archivos = os.listdir('.')
        for archivo in sorted(archivos):
            if archivo.endswith('.csv'):
                tamaño = os.path.getsize(archivo)
                print(f"  📄 {archivo} - {tamaño:,} bytes")
        
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ LA DESCARGA FALLÓ")
        print("=" * 60)
        
        # Crear archivo vacío como respaldo para no romper el pipeline
        print("\n📝 Creando archivo CSV vacío como respaldo...")
        with open('datos_actualizados.csv', 'w') as f:
            f.write('CUIT,CLIENTE,CAMPO,DEPARTAMENTO,LOCALIDAD,CULTIVO,LOTE\n')
            f.write('# Archivo vacío - Descarga falló\n')
        
        print("⚠️  Se creó archivo CSV vacío para continuar el pipeline")
        sys.exit(1)  # Salir con error pero con archivo creado

# ============================================
# 6. EJECUTAR
# ============================================
if __name__ == "__main__":
    main()
