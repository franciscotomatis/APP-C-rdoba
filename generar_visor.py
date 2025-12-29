import geopandas as gpd
import pandas as pd
import json
import folium
from folium import GeoJson
from folium.plugins import Fullscreen, MeasureControl
import os
import hashlib

print("🌱 GENERADOR DE APLICACIÓN WEB - PROGRAMA CÓRDOBA 25/26")
print("=" * 70)

# --- CAMBIO 1: TOMAR EL GEOJSON AUTOMÁTICO ---
GEOJSON_AUTOMATICO = "poligonos.geojson"  # Archivo generado por el proceso automático

# 🔐 CREDENCIALES DE ACCESO PARA LA APP WEB (mantenemos estas para el HTML)
USUARIO_CORRECTO = "Sancor"
CONTRASENA_CORRECTA = "2025Sancor"

# 🔐 GENERAR HASHES SEGUROS PARA LAS CREDENCIALES (para el HTML)
def generar_hash_seguro(texto):
    """Genera hash SHA-256 con salt para mayor seguridad"""
    salt = "ProgramaCordoba25/26-SancorSeguro"
    hash_obj = hashlib.sha256(f"{texto}{salt}".encode())
    return hash_obj.hexdigest()[:16]

# Hashes de las credenciales (NO se muestran en texto plano)
HASH_USUARIO = generar_hash_seguro(USUARIO_CORRECTO)
HASH_CONTRASENA = generar_hash_seguro(CONTRASENA_CORRECTA)

print(f"✅ Configurando aplicación con geojson automático: {GEOJSON_AUTOMATICO}")

def crear_app_geojson():
    """Crea la aplicación web usando el geojson generado automáticamente"""
    
    # --- CAMBIO 2: VERIFICAR SI EL ARCHIVO EXISTE ---
    if not os.path.exists(GEOJSON_AUTOMATICO):
        print(f"❌ Error: No se encontró el archivo {GEOJSON_AUTOMATICO}")
        print("💡 Espere a que se ejecute el proceso automático de descarga")
        return
    
    try:
        # 📖 CARGAR EL GEOJSON AUTOMÁTICO
        print(f"📖 Cargando {GEOJSON_AUTOMATICO}...")
        
        # Cargar GeoJSON
        with open(GEOJSON_AUTOMATICO, 'r') as f:
            geojson_data = json.load(f)
        
        # Convertir a GeoDataFrame para análisis
        gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
        gdf.crs = "EPSG:4326"
        
        print(f"✅ GeoJSON cargado: {len(gdf)} polígonos")
        
        # 🔍 BUSCAR CAMPOS CLAVE
        campo_cultivo = None
        for campo in ['CULTIVO', 'cultivo', 'Cultivo', 'CROP', 'crop']:
            if campo in gdf.columns:
                campo_cultivo = campo
                break
        
        campo_hectareas = None
        for campo in ['HECTAREAS_ASEGURADAS', 'HECTAREAS_DECLARADAS', 'hectareas', 'HECTAREAS', 'HAS', 'has']:
            if campo in gdf.columns:
                campo_hectareas = campo
                break
        
        campo_cliente = None
        for campo in ['CLIENTE', 'cliente', 'Cliente', 'NOMBRE_CLIENTE']:
            if campo in gdf.columns:
                campo_cliente = campo
                break
        
        campo_zona = None
        for campo in ['ZONA_CZ4', 'ZONA', 'Zona', 'zona', 'CZ4']:
            if campo in gdf.columns:
                campo_zona = campo
                break
        
        print(f"\n✅ Campos encontrados:")
        if campo_cultivo:
            print(f"   • Cultivo: '{campo_cultivo}'")
        if campo_hectareas:
            print(f"   • Hectáreas: '{campo_hectareas}'")
        if campo_cliente:
            print(f"   • Cliente: '{campo_cliente}'")
        if campo_zona:
            print(f"   • Zona (CZ4): '{campo_zona}'")
            zonas_unicas = sorted(gdf[campo_zona].dropna().unique())
            print(f"   • Zonas encontradas: {zonas_unicas}")
        
        if campo_cliente:
            clientes_unicos = sorted(gdf[campo_cliente].dropna().unique())
            print(f"\n📋 CLIENTES ENCONTRADOS ({len(clientes_unicos)}):")
            for i, cliente in enumerate(clientes_unicos[:15], 1):
                print(f"   {i:2d}. {cliente}")
            if len(clientes_unicos) > 15:
                print(f"   ... y {len(clientes_unicos)-15} más")
        
        # 🧮 CALCULAR SUPERFICIE EXACTA
        if campo_cultivo and campo_hectareas:
            gdf[campo_hectareas] = pd.to_numeric(gdf[campo_hectareas], errors='coerce')
            gdf[campo_hectareas] = gdf[campo_hectareas].fillna(0)
            
            print(f"\n📊 SUPERFICIE POR CULTIVO:")
            print(f"{'CULTIVO':<25} {'HECTÁREAS':>15} {'%':>8}")
            print(f"{'-'*25} {'-'*15} {'-'*8}")
            
            total_superficie = 0
            superficie_por_cultivo = {}
            
            for cultivo in gdf[campo_cultivo].dropna().unique():
                mascara = gdf[campo_cultivo] == cultivo
                hectareas = gdf.loc[mascara, campo_hectareas].sum()
                superficie_por_cultivo[cultivo] = hectareas
                total_superficie += hectareas
            
            for cultivo, hectareas in sorted(superficie_por_cultivo.items(), 
                                           key=lambda x: x[1], reverse=True):
                porcentaje = (hectareas / total_superficie * 100) if total_superficie > 0 else 0
                print(f"{str(cultivo)[:24]:<25} {hectareas:>15,.2f} {porcentaje:>7.1f}%")
            
            print(f"{'='*48}")
            print(f"{'TOTAL':<25} {total_superficie:>15,.2f} {100:>7.1f}%")
        
        # 📊 CALCULAR HECTÁREAS POR ZONA (PARA COMPARACIÓN)
        hectareas_por_zona = {}
        if campo_zona and campo_hectareas:
            gdf[campo_hectareas] = pd.to_numeric(gdf[campo_hectareas], errors='coerce')
            gdf[campo_hectareas] = gdf[campo_hectareas].fillna(0)
            
            # Convertir zona a string para consistencia
            gdf[campo_zona] = gdf[campo_zona].astype(str).str.strip()
            
            for zona in gdf[campo_zona].dropna().unique():
                zona_str = str(zona).strip()
                mascara = gdf[campo_zona] == zona_str
                hectareas = gdf.loc[mascara, campo_hectareas].sum()
                hectareas_por_zona[zona_str] = hectareas
            
            print(f"\n📊 HECTÁREAS POR ZONA (CZ4):")
            for zona in sorted(hectareas_por_zona.keys()):
                print(f"   Zona {zona}: {hectareas_por_zona[zona]:,.2f} ha")
        
        # 🗺️ CREAR MAPA
        print(f"\n🗺️ Creando aplicación web...")
        
        # Centro y bounds del mapa
        if not gdf.empty:
            minx, miny, maxx, maxy = gdf.total_bounds
            bounds = [[miny, minx], [maxy, maxx]]
            center = [(miny + maxy) / 2, (minx + maxx) / 2]
        else:
            center = [-31.4201, -64.1888]
            bounds = [[center[0]-0.1, center[1]-0.1], [center[0]+0.1, center[1]+0.1]]
        
        m = folium.Map(
            location=center,
            zoom_start=11,
            control_scale=True,
            tiles=None,
            zoom_control=True
        )

        # 🔧 CAPAS DE MAPA (3 NORMALES + 1 OSCURA)
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google',
            name='🌍 Google Satélite',
            max_zoom=20,
            overlay=False,
            control=True
        ).add_to(m)
        
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
            attr='Google',
            name='🗺️ Google Híbrido',
            max_zoom=20,
            overlay=False,
            control=True
        ).add_to(m)

        folium.TileLayer(
            tiles='https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
            attr='© CartoDB',
            name='🌙 Modo oscuro',
            overlay=False,
            control=True
        ).add_to(m)

        folium.TileLayer(
            tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attr='© OpenStreetMap',
            name='🌐 OpenStreetMap',
            overlay=False,
            control=True
        ).add_to(m)
        
        # 🎨 FUNCIÓN DE ESTILO POR CULTIVO
        def estilo_por_cultivo(feature):
            propiedades = feature['properties']
            
            color_relleno = '#9C27B0'
            color_borde = '#7B1FA2'
            
            if campo_cultivo and campo_cultivo in propiedades:
                cultivo = str(propiedades[campo_cultivo]).lower()
                
                if 'soja' in cultivo or 'soya' in cultivo:
                    color_relleno = '#4CAF50'
                    color_borde = '#2E7D32'
                elif 'maíz' in cultivo or 'maiz' in cultivo or 'corn' in cultivo:
                    color_relleno = '#FFC107'
                    color_borde = '#FF8F00'
                elif 'trigo' in cultivo or 'wheat' in cultivo:
                    color_relleno = '#795548'
                    color_borde = '#5D4037'
                elif 'girasol' in cultivo or 'sunflower' in cultivo:
                    color_relleno = '#FF9800'
                    color_borde = '#EF6C00'
                elif 'algodón' in cultivo or 'algodon' in cultivo or 'cotton' in cultivo:
                    color_relleno = '#2196F3'
                    color_borde = '#1976D2'
                elif 'sorgo' in cultivo or 'sorghum' in cultivo:
                    color_relleno = '#E91E63'
                    color_borde = '#C2185B'
            
            # Guardar colores en propiedades para restaurar después
            feature['properties']['_color_fill'] = color_relleno
            feature['properties']['_color_border'] = color_borde
            
            return {
                'fillColor': color_relleno,
                'color': color_borde,
                'weight': 2,
                'fillOpacity': 0.6,
                'dashArray': '5, 5'
            }
        
        def highlight_function(feature):
            return {
                'fillColor': '#FF5722',
                'color': '#D84315',
                'weight': 3,
                'fillOpacity': 0.8,
                'dashArray': '5, 5'
            }
        
        # 📋 CAMPOS PARA MOSTRAR
        campos_especificos = [
            'CUIT', 'CLIENTE', 'CAMPO', 'DEPARTAMENTO', 'LOCALIDAD', 'CULTIVO', 'LOTE',
            'CULTIVO_ANTERIOR', 'RENDIMIENTO_ANTERIOR', 'HECTAREAS_DECLARADAS',
            'HECTAREAS_ASEGURADAS', 'PORCENTAJE_ASEGURADO', 'ZONA_CZ4',
            'RENDIMIENTO_ASEGURADO', 'SUMA_ASEGURADA', 'FECHA_CREACION'
        ]
        
        campos_existentes = [campo for campo in campos_especificos if campo in gdf.columns]
        campos_numericos = [col for col in gdf.columns if pd.api.types.is_numeric_dtype(gdf[col])]
        otros_campos = [campo for campo in campos_numericos if campo not in campos_existentes and 'HECTAREAS' in campo]
        campos_para_popup = campos_existentes + otros_campos[:5]
        
        campos_tooltip = []
        if campo_cliente and campo_cliente in gdf.columns:
            campos_tooltip = [campo_cliente]
        elif campo_cultivo and campo_cultivo in gdf.columns:
            campos_tooltip = [campo_cultivo]
        else:
            campos_tooltip = ['excel_fila_num']
        
        # 🎯 CREAR CAPA GEOJSON
        geo_layer = folium.GeoJson(
            geojson_data,
            name='capa_poligonos_principal',
            style_function=estilo_por_cultivo,
            highlight_function=highlight_function,
            tooltip=folium.GeoJsonTooltip(
                fields=campos_tooltip,
                aliases=[f"{campo}" for campo in campos_tooltip],
                localize=True,
                sticky=True,
                style="""
                    font-family: Arial, sans-serif;
                    font-size: 11px;
                    background-color: rgba(255, 255, 255, 0.9);
                    border: 1px solid #4CAF50;
                    border-radius: 3px;
                    padding: 5px;
                """
            ),
            popup=folium.GeoJsonPopup(
                fields=campos_para_popup,
                aliases=[f"<b>{col}</b>" for col in campos_para_popup],
                localize=True,
                labels=True,
                style="""
                    font-family: Arial, sans-serif;
                    font-size: 11px;
                    max-height: 400px;
                    overflow-y: auto;
                    max-width: 350px;
                    padding: 10px;
                    background-color: #f8f9fa;
                    border: 2px solid #4CAF50;
                    border-radius: 5px;
                """
            )
        ).add_to(m)
        
        capa_nombre = geo_layer.get_name()
        
        # =================================================================
        # 🌧️ AGREGAR CAPAS WMS
        # =================================================================
        
        # IMERG DIARIO
        def agregar_capas_imerg():
            try:
                from owslib.wms import WebMapService
                import re
                from datetime import datetime
                
                url_wms = "https://geoservicios2.conae.gov.ar/geoserver/PrecipitacionAcumulada/wms"
                
                print("\n🔍 Conectando a IMERG diario...")
                
                wms = WebMapService(url_wms, version='1.3.0')
                
                capas_wms = ['MOM_GPMIMERG_PA1D_1', 'MOM_GPMIMERG_PA1D_2', 'MOM_GPMIMERG_PA1D_3']
                opacidades = [0.7, 0.6, 0.5]
                
                for i, capa_nombre_wms in enumerate(capas_wms):
                    if capa_nombre_wms in wms.contents:
                        capa_info = wms[capa_nombre_wms]
                        titulo = capa_info.title
                        
                        fecha_match = re.search(r'(\d{4}-\d{2}-\d{2})|(\d{2}/\d{2}/\d{4})', titulo)
                        
                        if fecha_match:
                            fecha_str = fecha_match.group(0)
                            try:
                                if '-' in fecha_str:
                                    fecha_dt = datetime.strptime(fecha_str, '%Y-%m-%d')
                                else:
                                    fecha_dt = datetime.strptime(fecha_str, '%d/%m/%Y')
                                fecha_formateada = fecha_dt.strftime('%d/%m')
                            except:
                                fecha_formateada = fecha_str
                            
                            nombre_display = f'🌧️ PP {fecha_formateada}'
                        else:
                            nombre_display = f'🌧️ PP Día {i+1}'
                        
                        folium.WmsTileLayer(
                            url=url_wms,
                            name=nombre_display,
                            layers=capa_nombre_wms,
                            fmt='image/png',
                            transparent=True,
                            opacity=opacidades[i],
                            overlay=True,
                            control=True,
                            show=False
                        ).add_to(m)
                        
                        print(f"✅ {nombre_display}")
                        
                    else:
                        print(f"⚠️ Capa {capa_nombre_wms} no disponible")
                
                print("✅ IMERG diario agregado")
                
            except Exception as e:
                print(f"⚠️ Error IMERG: {e}")
        
        # CHIRPS MENSUAL
        def agregar_capas_chirps():
            try:
                from owslib.wms import WebMapService
                import re
                from datetime import datetime
                
                url_wms_chirps = "https://geoservicios2.conae.gov.ar/geoserver/wms"
                
                print("\n🔍 Conectando a CHIRPS mensual...")
                
                wms_chirps = WebMapService(url_wms_chirps, version='1.3.0')
                
                capas_chirps = [
                    'PrecipitacionAcumulada:MOM_CHIRPS_PA1M_1',
                    'PrecipitacionAcumulada:MOM_CHIRPS_PA1M_2'
                ]
                
                opacidades_chirps = [0.5, 0.4]
                
                meses_espanol = {
                    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
                }
                
                for i, capa_nombre in enumerate(capas_chirps):
                    if capa_nombre in wms_chirps.contents:
                        capa_info = wms_chirps[capa_nombre]
                        titulo = capa_info.title
                        
                        fecha_match = re.search(r'(\d{4})-(\d{2})', titulo)
                        
                        if fecha_match:
                            año = int(fecha_match.group(1))
                            mes = int(fecha_match.group(2))
                            
                            if 1 <= mes <= 12 and 2000 <= año <= 2100:
                                nombre_mes = meses_espanol.get(mes, f"Mes {mes}")
                                nombre_display = f'📅 PP Acum {nombre_mes} {año}'
                            else:
                                nombre_display = f'📅 CHIRPS Mes {"Actual" if i == 0 else "Anterior"}'
                        else:
                            nombre_display = f'📅 CHIRPS Mes {"Actual" if i == 0 else "Anterior"}'
                        
                        folium.WmsTileLayer(
                            url=url_wms_chirps,
                            name=nombre_display,
                            layers=capa_nombre,
                            fmt='image/png',
                            transparent=True,
                            opacity=opacidades_chirps[i],
                            overlay=True,
                            control=True,
                            show=False
                        ).add_to(m)
                        
                        print(f"✅ {nombre_display}")
                        
                    else:
                        print(f"⚠️ Capa {capa_nombre} no disponible")
                
                print("✅ CHIRPS mensual agregado")
                
            except Exception as e:
                print(f"⚠️ Error CHIRPS: {e}")
        
        # EJECUTAR AMBAS FUNCIONES
        agregar_capas_imerg()
        agregar_capas_chirps()

        # =================================================================
        # 📊 LEYENDA DE PRECIPITACIÓN
        # =================================================================
        leyenda_precip_html = '''
        <div id="leyendaPrecip" style="position: fixed; 
                bottom: 40px; left: 10px;
                background-color: rgba(255, 255, 255, 0.98);
                padding: 10px 14px;
                border-radius: 8px;
                border: 2px solid #1E88E5;
                z-index: 9996;
                font-family: Arial, sans-serif;
                font-size: 11px;
                width: 140px;
                display: none;
                box-shadow: 0 4px 15px rgba(0,0,0,0.25);
                max-height: 400px;
                overflow-y: auto;">
            
            <div style="font-weight: bold; color: #1E88E5; 
                        margin-bottom: 10px; border-bottom: 2px solid #1E88E5; 
                        padding-bottom: 6px; font-size: 10px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 6px;">
                        <span>🌧️</span>
                        <span>Precipitación (mm)</span>
                    </div>
                    <button onclick="ocultarLeyendaPrecip()" 
                            style="background: none; border: none; color: #1E88E5; 
                                   font-size: 16px; cursor: pointer; padding: 0; 
                                   line-height: 1;">×</button>
                </div>
            </div>
            
            <!-- ESCALA DE COLORES -->
            <div style="margin-bottom: 10px;">
              
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <div style="width: 18px; height: 18px; background-color: #9e9eFF; 
                                margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                    <div style="flex: 1; display: flex; justify-content: space-between;">
                        <span style="font-size: 10px;">0</span>
                        <span style="font-size: 10px; color: #666;">mm</span>
                        <span style="font-size: 10px;">2</span>
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <div style="width: 18px; height: 18px; background-color: #0000FF; 
                                margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                    <div style="flex: 1; display: flex; justify-content: space-between;">
                        <span style="font-size: 10px;">2</span>
                        <span style="font-size: 10px; color: #666;">mm</span>
                        <span style="font-size: 10px;">5</span>
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <div style="width: 18px; height: 18px; background-color: #00FFFF; 
                                margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                    <div style="flex: 1; display: flex; justify-content: space-between;">
                        <span style="font-size: 10px;">5</span>
                        <span style="font-size: 10px; color: #666;">mm</span>
                        <span style="font-size: 10px;">10</span>
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <div style="width: 18px; height: 18px; background-color: #00FF80; 
                                margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                    <div style="flex: 1; display: flex; justify-content: space-between;">
                        <span style="font-size: 10px;">10</span>
                        <span style="font-size: 10px; color: #666;">mm</span>
                        <span style="font-size: 10px;">15</span>
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <div style="width: 18px; height: 18px; background-color: #00FF00; 
                                margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                    <div style="flex: 1; display: flex; justify-content: space-between;">
                        <span style="font-size: 10px;">15</span>
                        <span style="font-size: 10px; color: #666;">mm</span>
                        <span style="font-size: 10px;">20</span>
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <div style="width: 18px; height: 18px; background-color: #FFFF00; 
                                margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                    <div style="flex: 1; display: flex; justify-content: space-between;">
                        <span style="font-size: 10px;">20</span>
                        <span style="font-size: 10px; color: #666;">mm</span>
                        <span style="font-size: 10px;">30</span>
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <div style="width: 18px; height: 18px; background-color: #FFA500; 
                                margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                    <div style="flex: 1; display: flex; justify-content: space-between;">
                        <span style="font-size: 10px;">30</span>
                        <span style="font-size: 10px; color: #666;">mm</span>
                        <span style="font-size: 10px;">50</span>
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <div style="width: 18px; height: 18px; background-color: #FF4500; 
                                margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                    <div style="flex: 1; display: flex; justify-content: space-between;">
                        <span style="font-size: 10px;">50</span>
                        <span style="font-size: 10px; color: #666;">mm</span>
                        <span style="font-size: 10px;">100</span>
                    </div>
                </div>
                
                <div style="display: flex; align-items: center;">
                    <div style="width: 18px; height: 18px; background-color: #FF0000; 
                                margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                    <div style="flex: 1; display: flex; justify-content: space-between;">
                        <span style="font-size: 10px; font-weight: bold;">> 100</span>
                        <span style="font-size: 10px; color: #666;">mm</span>
                        <span style="font-size: 10px; font-weight: bold;"></span>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
        // Funciones para controlar la leyenda
        function actualizarLeyendaPrecip() {
            var leyenda = document.getElementById("leyendaPrecip");
            var checkboxes = document.querySelectorAll('input[type="checkbox"]');
            var capaPrecipActiva = false;
            
            checkboxes.forEach(function(checkbox) {
                var label = checkbox.parentElement;
                if (label && label.textContent) {
                    var textoLabel = label.textContent;
                    // Activar para IMERG (🌧️ PP) Y para CHIRPS (📅 PP)
                    if (textoLabel.includes("🌧️ PP") || textoLabel.includes("📅 PP")) {
                        if (checkbox.checked) {
                            capaPrecipActiva = true;
                        }
                    }
                }
            });
            
            if (capaPrecipActiva) {
                leyenda.style.display = "block";
            } else {
                leyenda.style.display = "none";
            }
        }
        
        function ocultarLeyendaPrecip() {
            document.getElementById("leyendaPrecip").style.display = "none";
        }
        
        // Inicializar
        document.addEventListener("DOMContentLoaded", function() {
            setTimeout(function() {
                var checkboxes = document.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(function(checkbox) {
                    checkbox.addEventListener("change", actualizarLeyendaPrecip);
                });
                
                if (typeof map !== "undefined") {
                    map.on("overlayadd overlayremove", function(e) {
                        if (e.name && (e.name.includes("🌧️ PP") || e.name.includes("📅 PP"))) {
                            setTimeout(actualizarLeyendaPrecip, 100);
                        }
                    });
                }
                
                setTimeout(actualizarLeyendaPrecip, 500);
            }, 1500);
        });
        </script>
        '''
        
        # Agregar la leyenda al mapa
        m.get_root().html.add_child(folium.Element(leyenda_precip_html))
        
        # 🔍 AJUSTAR VISTA
        if not gdf.empty:
            m.fit_bounds(bounds)           

        # 📊 CONTROLES
        folium.LayerControl(position='topright', collapsed=True).add_to(m)
        Fullscreen(
            position='topright',
            title='Pantalla completa',
            title_cancel='Salir pantalla completa'
        ).add_to(m)
        MeasureControl(position='topright').add_to(m)
        
        # 🔍 AJUSTAR VISTA
        if not gdf.empty:
            m.fit_bounds(bounds)
        
        # 🎨 TÍTULO MEJORADO
        from datetime import datetime
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        
        titulo_html = f'''
        <div style="position: fixed; 
                    top: 10px; left: 10px;
                    background-color: rgba(255, 255, 255, 0.95);
                    padding: 6px 10px;
                    border-radius: 4px;
                    border: 1px solid #4CAF50;
                    z-index: 9999;
                    font-family: Arial, sans-serif;
                    font-size: 10px;
                    max-width: 200px;
                    min-width: 180px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="font-weight: bold; color: #2E7D32; font-size: 14px; 
                        margin-bottom: 4px;">
                PROGRAMA CÓRDOBA 25/26
            </div>
            <div style="margin-top: 4px; font-size: 9px; color: #555; 
                        border-top: 1px solid #e0e0e0; padding-top: 4px;">
                <div><b>Fecha:</b> {fecha_actual}</div>
                <div><b>Polígonos:</b> {len(gdf)}</div>
                <div><b>Total Ha:</b> {total_superficie if 'total_superficie' in locals() else 0:,.0f}</div>
            </div>
        </div>
        '''
        
        m.get_root().html.add_child(folium.Element(titulo_html))
        
        # 🎨 LEYENDA DE CULTIVOS CON SUPERFICIE
        if campo_cultivo and campo_hectareas and 'superficie_por_cultivo' in locals():
            cultivos_ordenados = sorted(gdf[campo_cultivo].dropna().unique(),
                                      key=lambda x: superficie_por_cultivo.get(x, 0),
                                      reverse=True)[:8]
            
            items_leyenda = []
            for cultivo in cultivos_ordenados:
                cultivo_str = str(cultivo)
                hectareas = superficie_por_cultivo.get(cultivo, 0)
                porcentaje = (hectareas / total_superficie * 100) if total_superficie > 0 else 0
                
                color = '#9C27B0'
                cultivo_lower = cultivo_str.lower()
                
                if 'soja' in cultivo_lower or 'soya' in cultivo_lower:
                    color = '#4CAF50'
                elif 'maíz' in cultivo_lower or 'maiz' in cultivo_lower or 'corn' in cultivo_lower:
                    color = '#FFC107'
                elif 'trigo' in cultivo_lower or 'wheat' in cultivo_lower:
                    color = '#795548'
                elif 'girasol' in cultivo_lower or 'sunflower' in cultivo_lower:
                    color = '#FF9800'
                elif 'algodón' in cultivo_lower or 'algodon' in cultivo_lower or 'cotton' in cultivo_lower:
                    color = '#2196F3'
                elif 'sorgo' in cultivo_lower or 'sorghum' in cultivo_lower:
                    color = '#E91E63'
                
                texto_cultivo = f"{cultivo_str[:15]}{'...' if len(cultivo_str) > 15 else ''}"
                texto_superficie = f"{hectareas:,.0f}ha ({porcentaje:.0f}%)"
                
                items_leyenda.append(
                    f'<div style="display: flex; align-items: center; margin-bottom: 3px;">'
                    f'<div style="width: 12px; height: 12px; background-color: {color}; '
                    f'margin-right: 6px; border: 1px solid #333; border-radius: 2px; flex-shrink: 0;"></div>'
                    f'<div style="flex: 1; display: flex; justify-content: space-between; align-items: center;">'
                    f'<span style="font-size: 10px; font-weight: bold;">{texto_cultivo}</span>'
                    f'<span style="font-size: 9px; color: #666; margin-left: 5px;">{texto_superficie}</span>'
                    f'</div>'
                    f'</div>'
                )
            
            items_leyenda.append(
                f'<div style="margin-top: 6px; padding-top: 4px; border-top: 1px solid #4CAF50; '
                f'font-size: 10px; font-weight: bold; color: #2E7D32; text-align: center;">'
                f'TOTAL: {total_superficie:,.0f} ha'
                f'</div>'
            )
            
            leyenda_html = f'''
            <div style="position: fixed; 
                        bottom: 10px; right: 10px;
                        background-color: rgba(255, 255, 255, 0.98);
                        padding: 6px 8px;
                        border-radius: 4px;
                        border: 1px solid #4CAF50;
                        z-index: 9999;
                        font-family: Arial, sans-serif;
                        font-size: 11px;
                        width: 160px;
                        max-height: 200px;
                        overflow-y: auto;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
                <div style="font-weight: bold; color: #2E7D32; margin-bottom: 6px; 
                            font-size: 11px; border-bottom: 1px solid #ddd; padding-bottom: 3px;">
                    Cultivos ({len(gdf[campo_cultivo].dropna().unique())})
                </div>
                {''.join(items_leyenda)}
            </div>
            '''
            
            m.get_root().html.add_child(folium.Element(leyenda_html))
        
        # 🔍 BUSCADOR DE CLIENTES
        if campo_cliente:
            clientes = sorted(gdf[campo_cliente].dropna().astype(str).unique())
            
            # Guardar los bounds generales para el reset
            bounds_general = geo_layer.get_bounds()
            
            # Crear el buscador DEBAJO DEL TÍTULO (IZQUIERDA)
            buscador_html = f'''
            <div id="lupitaBuscador" style="position: fixed; 
                  top: 100px; left: 10px;
                    background-color: rgba(255, 255, 255, 0.95);
                    padding: 8px 10px;
                    border-radius: 6px;
                    border: 1px solid #4CAF50;
                    z-index: 9998;
                    font-family: Arial, sans-serif;
                    font-size: 11px;
                    width: 220px;
                    box-shadow: 0 3px 8px rgba(0,0,0,0.15);
                    transition: all 0.3s ease;">
                
                <!-- CABECERA CON LUPITA -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-weight: bold; color: #000000; font-size: 12px; display: flex; align-items: center;">
                        <span style="margin-right: 5px;">🔍</span>
                        Buscar cliente
                    </div>
                    <button id="toggleBuscador" 
                            style="background: none; border: none; cursor: pointer; font-size: 14px; color: #000000;"
                            onclick="toggleBuscador()">▲</button>
                </div>
                
                <!-- CONTENIDO (inicialmente visible) -->
                <div id="contenidoBuscador">
                    <div style="margin-bottom: 8px;">
                        <input list="clientesList" 
                               id="clienteInput" 
                               placeholder="Escribe o selecciona..."
                               style="width: 100%; padding: 5px; border: 1px solid #ddd; 
                                      border-radius: 3px; font-size: 11px;">
                        <datalist id="clientesList">
                            {"".join(f'<option value="{cliente}">' for cliente in clientes)}
                        </datalist>
                    </div>
                    
                    <div style="display: flex; gap: 5px; margin-bottom: 6px;">
                        <button onclick="filtrarCliente()" 
                                style="flex: 1; background-color: #4CAF50; color: white; 
                                       border: none; padding: 5px; border-radius: 3px; 
                                       cursor: pointer; font-size: 10px;">
                            Filtrar
                        </button>
                        <button onclick="resetearFiltro()" 
                                style="flex: 1; background-color: #f44336; color: white; 
                                       border: none; padding: 5px; border-radius: 3px; 
                                       cursor: pointer; font-size: 10px;">
                            Reset
                        </button>
                    </div>
                    
                    <div id="estadoFiltro" 
                         style="font-size: 9px; color: #666; margin-top: 6px; 
                                padding-top: 5px; border-top: 1px solid #000000;">
                        Mostrando todos ({len(gdf)})
                    </div>
                </div>
            </div>
            
            <script>
            // Variables globales
            var boundsGeneral = {capa_nombre}.getBounds();
            var contenidoVisible = true;
            var mapaPoligonos = new Map();
            
            // Función para mostrar/ocultar contenido
            function toggleBuscador() {{
                var contenido = document.getElementById("contenidoBuscador");
                var toggleBtn = document.getElementById("toggleBuscador");
                var lupita = document.getElementById("lupitaBuscador");
                
                if (contenidoVisible) {{
                    contenido.style.display = "none";
                    toggleBtn.innerHTML = "▼";
                    lupita.style.width = "150px";
                    lupita.style.padding = "5px 8px";
                }} else {{
                    contenido.style.display = "block";
                    toggleBtn.innerHTML = "▲";
                    lupita.style.width = "220px";
                    lupita.style.padding = "8px 10px";
                }}
                contenidoVisible = !contenidoVisible;
            }}
            
            // Almacenar referencia a cada polígono al inicio
            function inicializarPoligonos() {{
                {capa_nombre}.eachLayer(function(layer) {{
                    var id = layer._leaflet_id;
                    mapaPoligonos.set(id, layer);
                    
                    // Guardar estilo original
                    layer._estiloOriginal = {{
                        fillColor: layer.options.fillColor,
                        color: layer.options.color,
                        weight: layer.options.weight,
                        fillOpacity: layer.options.fillOpacity,
                        opacity: layer.options.opacity,
                        interactive: layer.options.interactive
                    }};
                }});
            }}
            
            // Función para filtrar
            function filtrarCliente() {{
                var valor = document.getElementById("clienteInput").value.toLowerCase();
                if (!valor) {{
                    alert("Por favor, escribe o selecciona un cliente");
                    return;
                }}
                
                var boundsFiltrados = null;
                var contador = 0;
                
                // Recorrer TODOS los polígonos de la capa
                {capa_nombre}.eachLayer(function(layer) {{
                    var propiedades = layer.feature.properties;
                    var clienteEnPoligono = propiedades["{campo_cliente}"];
                    
                    // Verificar si coincide (búsqueda parcial)
                    if (clienteEnPoligono && clienteEnPoligono.toString().toLowerCase().includes(valor)) {{
                        // MOSTRAR este polígono completamente
                        layer.setStyle({{
                            fillOpacity: 0.6,
                            weight: 2,
                            opacity: 1
                        }});
                        
                        // Hacerlo interactivo
                        layer.options.interactive = true;
                        
                        // Restaurar tooltip y popup
                        if (layer._tooltip) {{
                            layer._tooltip.options.interactive = true;
                        }}
                        
                        // Agregar a bounds para zoom
                        var layerBounds = layer.getBounds();
                        if (layerBounds) {{
                            if (!boundsFiltrados) {{
                                boundsFiltrados = layerBounds;
                            }} else {{
                                boundsFiltrados = boundsFiltrados.extend(layerBounds);
                            }}
                        }}
                        contador++;
                    }} else {{
                        // OCULTAR este polígono COMPLETAMENTE
                        layer.setStyle({{
                            fillOpacity: 0,
                            weight: 0,
                            opacity: 0
                        }});
                        
                        // DESHABILITAR completamente la interactividad
                        layer.options.interactive = false;
                        
                        // Deshabilitar tooltip
                        if (layer._tooltip) {{
                            layer._tooltip.options.interactive = false;
                            layer.unbindTooltip();
                        }}
                        
                        // Deshabilitar popup
                        if (layer._popup) {{
                            layer.unbindPopup();
                        }}
                        
                        // Remover event listeners de mouse
                        layer.off('mouseover');
                        layer.off('mouseout');
                        layer.off('click');
                    }}
                }});
                
                // Actualizar estado
                var estadoDiv = document.getElementById("estadoFiltro");
                if (contador > 0) {{
                    estadoDiv.innerHTML = "Mostrando " + contador + " polígonos";
                    estadoDiv.style.color = "#4CAF50";
                    
                    // Zoom a los polígonos filtrados
                    if (boundsFiltrados) {{
                        map.fitBounds(boundsFiltrados, {{padding: [50, 50]}});
                    }}
                }} else {{
                    estadoDiv.innerHTML = "❌ No se encontraron";
                    estadoDiv.style.color = "#f44336";
                }}
            }}
            
            // Función para resetear
            function resetearFiltro() {{
                // Limpiar input
                document.getElementById("clienteInput").value = "";
                
                // Mostrar TODOS los polígonos nuevamente y restaurar TODO
                {capa_nombre}.eachLayer(function(layer) {{
                    // Restaurar estilo original
                    if (layer._estiloOriginal) {{
                        layer.setStyle(layer._estiloOriginal);
                    }} else {{
                        // Si no hay estilo guardado, restaurar valores por defecto
                        var propiedades = layer.feature.properties;
                        layer.setStyle({{
                            fillColor: propiedades._color_fill || '#9C27B0',
                            color: propiedades._color_border || '#7B1FA2',
                            weight: 2,
                            fillOpacity: 0.6,
                            opacity: 1
                        }});
                    }}
                    
                    // RESTAURAR INTERACTIVIDAD COMPLETA
                    layer.options.interactive = true;
                    
                    // Restaurar tooltip si existía
                    if (!layer._tooltip && layer.feature.properties["{campo_cliente}"]) {{
                        layer.bindTooltip(layer.feature.properties["{campo_cliente}"], {{
                            sticky: true,
                            className: 'leaflet-tooltip-custom'
                        }});
                    }}
                    
                    // Restaurar event listeners
                    layer.on('mouseover', function(e) {{
                        e.target.setStyle({{
                            fillOpacity: 0.8,
                            weight: 3
                        }});
                    }});
                    
                    layer.on('mouseout', function(e) {{
                        {capa_nombre}.resetStyle(e.target);
                    }});
                }});
                
                // Forzar redibujado
                {capa_nombre}.redraw();
                
                // Restaurar zoom original
                if (boundsGeneral && boundsGeneral.isValid()) {{
                    map.fitBounds(boundsGeneral);
                }}
                
                // Actualizar estado
                var estadoDiv = document.getElementById("estadoFiltro");
                estadoDiv.innerHTML = "Mostrando todos ({len(gdf)})";
                estadoDiv.style.color = "#666";
            }}
            
            // Permitir usar Enter para filtrar
            document.getElementById("clienteInput").addEventListener("keypress", function(e) {{
                if (e.key === "Enter") {{
                    filtrarCliente();
                }}
            }});
            
            // Inicializar cuando se carga la página
            document.addEventListener("DOMContentLoaded", function() {{
                setTimeout(function() {{
                    inicializarPoligonos();
                }}, 1000);
            }});
            </script>
            '''
            
            m.get_root().html.add_child(folium.Element(buscador_html))
        
        # 📊 BOTÓN FLOTANTE PARA GRÁFICOS Y PANEL DESPLEGABLE
        # Hectáreas proyectadas por zona
        hectareas_proyectadas = {
            "1": 84940,
            "2": 155256,
            "3": 158675,
            "4": 134574
        }
        
        # Preparar datos para el gráfico
        zonas_ordenadas = ["1", "2", "3", "4"]
        datos_proyectados = []
        datos_reales = []
        diferencias = []
        porcentajes_dif = []
        
        for zona in zonas_ordenadas:
            proyectado = hectareas_proyectadas.get(zona, 0)
            real = hectareas_por_zona.get(zona, 0) if zona in hectareas_por_zona else 0
            diferencia = real - proyectado
            porcentaje = (diferencia / proyectado * 100) if proyectado > 0 else 0
            
            datos_proyectados.append(proyectado)
            datos_reales.append(real)
            diferencias.append(diferencia)
            porcentajes_dif.append(porcentaje)
        
        # Calcular máximos para escalado de barras
        max_valor = max(max(datos_proyectados), max(datos_reales)) if datos_proyectados and datos_reales else 100000
        
        panel_graficos_html = f'''
        <!-- BOTÓN FLOTANTE PARA ABRIR GRÁFICOS (SOLO ICONO) -->
        <div id="btnGraficos" style="position: fixed; 
                bottom: 20px; left: 20px;
                background-color: #2E7D32;
                color: white;
                padding: 12px;
                border-radius: 50%;
                z-index: 9997;
                cursor: pointer;
                box-shadow: 0 3px 10px rgba(0,0,0,0.2);
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: Arial, sans-serif;
                font-size: 24px;
                width: 50px;
                height: 50px;
                transition: background-color 0.3s, transform 0.2s;"
                onclick="togglePanelGraficos()"
                onmouseover="this.style.transform='scale(1.1)'"
                onmouseout="this.style.transform='scale(1)'">
            📊
        </div>
        
        <!-- PANEL DESPLEGABLE DE GRÁFICOS -->
        <div id="panelGraficos" style="position: fixed; 
                bottom: -85%;
                left: 0;
                width: 100%;
                height: 85%;
                background-color: white;
                z-index: 10001;
                box-shadow: 0 -3px 15px rgba(0,0,0,0.3);
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
                transition: bottom 0.4s ease;
                overflow-y: auto;
                font-family: Arial, sans-serif;">
            
            <!-- CABECERA DEL PANEL -->
            <div style="position: sticky; top: 0; background-color: #2E7D32; color: white; 
                        padding: 15px 20px; border-top-left-radius: 15px; border-top-right-radius: 15px;
                        display: flex; justify-content: space-between; align-items: center; z-index: 1;">
                <div style="font-size: 18px; font-weight: bold; display: flex; align-items: center; gap: 10px;">
                    <span>📊</span>
                    COMPARACIÓN POR ZONA - PROYECTADO vs ACTUAL
                </div>
                <button onclick="togglePanelGraficos()" 
                        style="background: none; border: none; color: white; font-size: 24px; 
                               cursor: pointer; padding: 0; width: 30px; height: 30px;">
                    ×
                </button>
            </div>
            
            <!-- CONTENIDO DEL PANEL -->
            <div style="padding: 20px; max-width: 1000px; margin: 0 auto;">
                
                <!-- RESUMEN -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                            gap: 15px; margin-bottom: 25px;">
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #2E7D32;">
                        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">TOTAL PROYECTADO</div>
                        <div style="font-size: 22px; font-weight: bold; color: #2E7D32;">
                            {sum(hectareas_proyectadas.values()):,.0f} ha
                        </div>
                    </div>
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3;">
                        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">TOTAL ACTUAL</div>
                        <div style="font-size: 22px; font-weight: bold; color: #2196F3;">
                            {sum(hectareas_por_zona.values()):,.0f} ha
                        </div>
                    </div>
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #FF9800;">
                        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">DIFERENCIA TOTAL</div>
                        <div style="font-size: 22px; font-weight: bold; color: { 'red' if (sum(hectareas_por_zona.values()) - sum(hectareas_proyectadas.values())) < 0 else '#4CAF50' };">
                            {sum(hectareas_por_zona.values()) - sum(hectareas_proyectadas.values()):+,.0f} ha
                        </div>
                    </div>
                    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #9C27B0;">
                        <div style="font-size: 12px; color: #666; margin-bottom: 5px;">% DE CUMPLIMIENTO</div>
                        <div style="font-size: 22px; font-weight: bold; color: { 'red' if ((sum(hectareas_por_zona.values()) / sum(hectareas_proyectadas.values()) * 100) if sum(hectareas_proyectadas.values()) > 0 else 0) < 100 else '#4CAF50' };">
                            {(sum(hectareas_por_zona.values()) / sum(hectareas_proyectadas.values()) * 100) if sum(hectareas_proyectadas.values()) > 0 else 0:.1f}%
                        </div>
                    </div>
                </div>
                
                <!-- GRÁFICO DE BARRAS AGRUPADAS -->
                <div style="background-color: white; border: 1px solid #e0e0e0; border-radius: 8px; 
                            padding: 20px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <h3 style="margin-top: 0; margin-bottom: 20px; color: #333; font-size: 16px; 
                              border-bottom: 2px solid #2E7D32; padding-bottom: 8px;">
                        HECTÁREAS POR ZONA - COMPARACIÓN
                    </h3>
                    
                    <div style="display: flex; flex-direction: column; gap: 20px;">
        '''
        
        # Generar barras para cada zona
        for i, zona in enumerate(zonas_ordenadas):
            proyectado = datos_proyectados[i]
            real = datos_reales[i]
            diferencia = diferencias[i]
            porcentaje = porcentajes_dif[i]
            
            # Calcular anchos relativos
            ancho_proyectado = min(95, (proyectado / max_valor * 95))
            ancho_real = min(95, (real / max_valor * 95))
            
            # Determinar colores según diferencia
            color_proyectado = "#2E7D32"
            color_real = "#2196F3" if diferencia >= 0 else "#f44336"
            color_diferencia = "#4CAF50" if diferencia >= 0 else "#f44336"
            icono_diferencia = "↗️" if diferencia >= 0 else "↘️"
            
            panel_graficos_html += f'''
                        <!-- ZONA {zona} -->
                        <div style="margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <div style="font-weight: bold; color: #333; font-size: 14px;">
                                    ZONA {zona}
                                </div>
                                <div style="font-size: 13px; color: #666;">
                                    Diferencia: <span style="font-weight: bold; color: {color_diferencia}">
                                        {diferencia:+,.0f} ha ({porcentaje:+.1f}%) {icono_diferencia}
                                    </span>
                                </div>
                            </div>
                            
                            <!-- BARRA PROYECTADO -->
                            <div style="margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                                    <span style="font-size: 12px; color: #666;">Proyectado</span>
                                    <span style="font-size: 12px; font-weight: bold; color: {color_proyectado}">
                                        {proyectado:,.0f} ha
                                    </span>
                                </div>
                                <div style="width: 100%; background-color: #f0f0f0; border-radius: 4px; height: 24px; overflow: hidden;">
                                    <div style="width: {ancho_proyectado}%; height: 100%; background-color: {color_proyectado}; 
                                            border-radius: 4px; display: flex; align-items: center; padding-left: 10px;">
                                        <span style="color: white; font-size: 11px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
                                            PROYECTADO
                                        </span>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- BARRA ACTUAL -->
                            <div style="margin-bottom: 15px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                                    <span style="font-size: 12px; color: #666;">Actual</span>
                                    <span style="font-size: 12px; font-weight: bold; color: {color_real}">
                                        {real:,.0f} ha
                                    </span>
                                </div>
                                <div style="width: 100%; background-color: #f0f0f0; border-radius: 4px; height: 24px; overflow: hidden;">
                                    <div style="width: {ancho_real}%; height: 100%; background-color: {color_real}; 
                                            border-radius: 4px; display: flex; align-items: center; padding-left: 10px;">
                                        <span style="color: white; font-size: 11px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
                                            ACTUAL
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
            '''
        
        # Tabla resumen
        panel_graficos_html += f'''
                    </div>
                </div>
                
                <!-- TABLA RESUMEN -->
                <div style="background-color: white; border: 1px solid #e0e0e0; border-radius: 8px; 
                            padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <h3 style="margin-top: 0; margin-bottom: 15px; color: #333; font-size: 16px;">
                        RESUMEN
                    </h3>
                    
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                            <thead>
                                <tr style="background-color: #f5f5f5;">
                                    <th style="padding: 10px; text-align: left; border-bottom: 2px solid #2E7D32;">ZONA</th>
                                    <th style="padding: 10px; text-align: right; border-bottom: 2px solid #2E7D32;">PROYECTADO (ha)</th>
                                    <th style="padding: 10px; text-align: right; border-bottom: 2px solid #2E7D32;">ACTUAL (ha)</th>
                                    <th style="padding: 10px; text-align: right; border-bottom: 2px solid #2E7D32;">DIFERENCIA (ha)</th>
                                    <th style="padding: 10px; text-align: right; border-bottom: 2px solid #2E7D32;">% VARIACIÓN</th>
                                </tr>
                            </thead>
                            <tbody>
        '''
        
        for i, zona in enumerate(zonas_ordenadas):
            proyectado = datos_proyectados[i]
            real = datos_reales[i]
            diferencia = diferencias[i]
            porcentaje = porcentajes_dif[i]
            
            color_diferencia = "#4CAF50" if diferencia >= 0 else "#f44336"
            
            panel_graficos_html += f'''
                                <tr style="border-bottom: 1px solid #eee;">
                                    <td style="padding: 10px; font-weight: bold;">Zona {zona}</td>
                                    <td style="padding: 10px; text-align: right;">{proyectado:,.0f}</td>
                                    <td style="padding: 10px; text-align: right; font-weight: bold;">{real:,.0f}</td>
                                    <td style="padding: 10px; text-align: right; color: {color_diferencia}; font-weight: bold;">
                                        {diferencia:+,.0f}
                                    </td>
                                    <td style="padding: 10px; text-align: right; color: {color_diferencia};">
                                        {porcentaje:+.1f}%
                                    </td>
                                </tr>
            '''
        
        panel_graficos_html += f'''
                            </tbody>
                            <tfoot style="background-color: #f9f9f9; font-weight: bold;">
                                <tr>
                                    <td style="padding: 10px; border-top: 2px solid #2E7D32;">TOTAL</td>
                                    <td style="padding: 10px; text-align: right; border-top: 2px solid #2E7D32;">
                                        {sum(datos_proyectados):,.0f}
                                    </td>
                                    <td style="padding: 10px; text-align: right; border-top: 2px solid #2E7D32;">
                                        {sum(datos_reales):,.0f}
                                    </td>
                                    <td style="padding: 10px; text-align: right; border-top: 2px solid #2E7D32; 
                                        color: {'#4CAF50' if (sum(datos_reales) - sum(datos_proyectados)) >= 0 else '#f44336'};">
                                        {sum(datos_reales) - sum(datos_proyectados):+,.0f}
                                    </td>
                                    <td style="padding: 10px; text-align: right; border-top: 2px solid #2E7D32;
                                        color: {'#4CAF50' if ((sum(datos_reales) / sum(datos_proyectados) * 100) - 100 if sum(datos_proyectados) > 0 else 0) >= 0 else '#f44336'};">
                                        {((sum(datos_reales) / sum(datos_proyectados) * 100) - 100) if sum(datos_proyectados) > 0 else 0:+.1f}%
                                    </td>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
                </div>
                
                <!-- INFORMACIÓN ADICIONAL -->
                <div style="font-size: 12px; color: #666; padding: 15px; background-color: #f8f9fa; 
                            border-radius: 6px; border-left: 4px solid #FF9800;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                        <span>💡</span>
                        <strong>Información para el análisis:</strong>
                    </div>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>Datos proyectados: valores estimados para la campaña 25/26</li>
                        <li>Datos actuales: calculados automáticamente del archivo GeoJSON cargado</li>
                        <li>Verde (↑): la zona supera la proyección</li>
                        <li>Rojo (↓): la zona está por debajo de la proyección</li>
                        <li>Actualizado automáticamente desde Multiriesgo</li>
                    </ul>
                </div>
                
            </div>
        </div>
        
        <style>
            #panelGraficos {{
                scrollbar-width: thin;
                scrollbar-color: #2E7D32 #f0f0f0;
            }}
            
            #panelGraficos::-webkit-scrollbar {{
                width: 8px;
            }}
            
            #panelGraficos::-webkit-scrollbar-track {{
                background: #f0f0f0;
                border-radius: 4px;
            }}
            
            #panelGraficos::-webkit-scrollbar-thumb {{
                background-color: #2E7D32;
                border-radius: 4px;
            }}
            
            #panelGraficos[style*="bottom: 0"] {{
                z-index: 10001 !important;
            }}
            
            #btnGraficos {{
                z-index: 10002 !important;
            }}
            
            div[style*="top: 10px; left: 10px"] {{
                z-index: 9999;
            }}
            
            div[style*="bottom: 10px; right: 10px"] {{
                z-index: 9999;
            }}
            
            #lupitaBuscador {{
                z-index: 9999;
            }}
            
            @media (max-width: 768px) {{
                #panelGraficos {{
                    height: 90%;
                    bottom: -90%;
                }}
                
                #btnGraficos {{
                    left: 15px;
                    bottom: 15px;
                    width: 45px;
                    height: 45px;
                    font-size: 20px;
                }}
            }}
        </style>
        
        <script>
            let panelAbierto = false;
            
            function togglePanelGraficos() {{
                const panel = document.getElementById("panelGraficos");
                const btn = document.getElementById("btnGraficos");
                
                if (panelAbierto) {{
                    // Cerrar panel
                    panel.style.bottom = "-85%";
                    panel.style.zIndex = "9998";
                    btn.innerHTML = "📊";
                    btn.style.backgroundColor = "#2E7D32";
                    
                }} else {{
                    // Abrir panel
                    panel.style.zIndex = "10001";
                    panel.style.bottom = "0";
                    btn.innerHTML = "📈";
                    btn.style.backgroundColor = "#2196F3";
                }}
                
                panelAbierto = !panelAbierto;
            }}
            
            // Cerrar panel al hacer clic fuera
            document.addEventListener('click', function(event) {{
                const panel = document.getElementById("panelGraficos");
                const btn = document.getElementById("btnGraficos");
                
                if (panelAbierto && !panel.contains(event.target) && !btn.contains(event.target)) {{
                    togglePanelGraficos();
                }}
            }});
        </script>
        '''
        
        m.get_root().html.add_child(folium.Element(panel_graficos_html))
        
        # 🔐 PANTALLA DE LOGIN CON HASH SEGURO
        login_html = f'''
        <div id="loginScreen" style="position: fixed; 
                top: 0; left: 0; 
                width: 100%; height: 100%; 
                background-color: rgba(255, 255, 255, 0.98);
                z-index: 10000;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                font-family: Arial, sans-serif;
                transition: opacity 0.5s ease;">
            
            <div style="background-color: white; 
                        padding: 40px; 
                        border-radius: 10px; 
                        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                        border: 3px solid #2E7D32;
                        text-align: center;
                        max-width: 400px;
                        width: 90%;">
                
                <div style="font-size: 32px; margin-bottom: 20px; color: #2E7D32;">
                    🔐
                </div>
                
                <h2 style="color: #2E7D32; margin-bottom: 10px;">
                    PROGRAMA CÓRDOBA 25/26
                </h2>
                
                <p style="color: #000000; margin-bottom: 30px; font-size: 14px;">
                    Acceso restringido
                </p>
                
                <div style="margin-bottom: 20px; text-align: left;">
                    <label style="display: block; margin-bottom: 5px; font-weight: bold; color: #333;">
                        👤 Usuario
                    </label>
                    <input type="text" id="loginUsuario" 
                           placeholder="Ingrese su usuario" 
                           style="width: 100%; padding: 12px; 
                                  border: 2px solid #ddd; 
                                  border-radius: 5px;
                                  font-size: 14px;
                                  box-sizing: border-box;">
                </div>
                
                <div style="margin-bottom: 30px; text-align: left;">
                    <label style="display: block; margin-bottom: 5px; font-weight: bold; color: #333;">
                        🔒 Contraseña
                    </label>
                    <input type="password" id="loginContrasena" 
                           placeholder="Ingrese su contraseña" 
                           style="width: 100%; padding: 12px; 
                                  border: 2px solid #ddd; 
                                  border-radius: 5px;
                                  font-size: 14px;
                                  box-sizing: border-box;">
                </div>
                
                <button onclick="verificarAcceso()" 
                        style="background-color: #2E7D32; 
                               color: white; 
                               border: none; 
                               padding: 14px 30px; 
                               border-radius: 5px; 
                               font-size: 16px; 
                               font-weight: bold;
                               cursor: pointer;
                               width: 100%;
                               transition: background-color 0.3s;">
                    🔓 INGRESAR AL SISTEMA
                </button>
                
                <div id="loginError" 
                     style="margin-top: 15px; 
                            color: #f44336; 
                            font-size: 13px; 
                            font-weight: bold;
                            display: none;">
                    ❌ Usuario o contraseña incorrectos
                </div>
                
                <div style="margin-top: 25px; font-size: 12px; color: #888; border-top: 1px solid #eee; padding-top: 15px;">
                    Sistema automatizado - Actualizado: {fecha_actual}
                </div>
            </div>
        </div>
        
        <script>
        // HASHES SEGUROS DE LAS CREDENCIALES
        const HASH_USUARIO_VALIDO = "{HASH_USUARIO}";
        const HASH_CONTRASENA_VALIDA = "{HASH_CONTRASENA}";
        
        // Función para calcular hash
        async function calcularHash(texto) {{
            const salt = "ProgramaCordoba25/26-SancorSeguro";
            const encoder = new TextEncoder();
            const data = encoder.encode(texto + salt);
            
            const hashBuffer = await crypto.subtle.digest('SHA-256', data);
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
            return hashHex.substring(0, 16);
        }}
        
        // Función principal de verificación
        async function verificarAcceso() {{
            const usuario = document.getElementById("loginUsuario").value.trim();
            const contrasena = document.getElementById("loginContrasena").value.trim();
            const errorDiv = document.getElementById("loginError");
            
            if (!usuario || !contrasena) {{
                errorDiv.innerHTML = "❌ Por favor, complete ambos campos";
                errorDiv.style.display = "block";
                return;
            }}
            
            try {{
                // Calcular hashes de lo ingresado
                const hashUsuarioIngresado = await calcularHash(usuario);
                const hashContrasenaIngresada = await calcularHash(contrasena);
                
                // Comparar hashes
                if (hashUsuarioIngresado === HASH_USUARIO_VALIDO && 
                    hashContrasenaIngresada === HASH_CONTRASENA_VALIDA) {{
                    
                    // Acceso concedido
                    document.getElementById("loginScreen").style.opacity = "0";
                    setTimeout(function() {{
                        document.getElementById("loginScreen").style.display = "none";
                    }}, 500);
                    
                    // Mostrar buscador
                    if (document.getElementById("lupitaBuscador")) {{
                        document.getElementById("lupitaBuscador").style.display = "block";
                    }}
                    
                    // Mostrar botón de gráficos
                    if (document.getElementById("btnGraficos")) {{
                        document.getElementById("btnGraficos").style.display = "flex";
                    }}
                    
                    // Habilitar mapa
                    map.getContainer().style.pointerEvents = "auto";
                    
                    // Guardar sesión (válida por 7 días)
                    localStorage.setItem('sesion_valida', 'true');
                    localStorage.setItem('ultimo_acceso', new Date().toISOString());
                    
                }} else {{
                    // Credenciales incorrectas
                    errorDiv.innerHTML = "❌ Usuario o contraseña incorrectos";
                    errorDiv.style.display = "block";
                    document.getElementById("loginContrasena").value = "";
                    document.getElementById("loginContrasena").focus();
                    
                    // Animación de error
                    const loginBox = document.getElementById("loginScreen").firstElementChild;
                    loginBox.style.animation = "shake 0.5s";
                    setTimeout(() => {{
                        loginBox.style.animation = "";
                    }}, 500);
                }}
            }} catch (error) {{
                errorDiv.innerHTML = "❌ Error al verificar credenciales";
                errorDiv.style.display = "block";
            }}
        }}
        
        // Verificar si ya tiene sesión activa
        function verificarSesionActiva() {{
            const sesionValida = localStorage.getItem('sesion_valida');
            const ultimoAcceso = localStorage.getItem('ultimo_acceso');
            
            if (sesionValida === 'true' && ultimoAcceso) {{
                const ultimaFecha = new Date(ultimoAcceso);
                const ahora = new Date();
                const diferenciaDias = (ahora - ultimaFecha) / (1000 * 60 * 60 * 24);
                
                // Sesión válida por 7 días
                if (diferenciaDias < 7) {{
                    document.getElementById("loginScreen").style.display = "none";
                    if (document.getElementById("lupitaBuscador")) {{
                        document.getElementById("lupitaBuscador").style.display = "block";
                    }}
                    if (document.getElementById("btnGraficos")) {{
                        document.getElementById("btnGraficos").style.display = "flex";
                    }}
                    map.getContainer().style.pointerEvents = "auto";
                    return true;
                }} else {{
                    // Sesión expirada
                    localStorage.removeItem('sesion_valida');
                    localStorage.removeItem('ultimo_acceso');
                }}
            }}
            return false;
        }}
        
        // Permitir Enter para login
        document.getElementById("loginUsuario").addEventListener("keypress", function(e) {{
            if (e.key === "Enter") {{
                document.getElementById("loginContrasena").focus();
            }}
        }});
        
        document.getElementById("loginContrasena").addEventListener("keypress", function(e) {{
            if (e.key === "Enter") {{
                verificarAcceso();
            }}
        }});
        
        // Estilos para animación
        const style = document.createElement('style');
        style.textContent = `
            @keyframes shake {{
                0%, 100% {{ transform: translateX(0); }}
                10%, 30%, 50%, 70%, 90% {{ transform: translateX(-5px); }}
                20%, 40%, 60%, 80% {{ transform: translateX(5px); }}
            }}
        `;
        document.head.appendChild(style);
        
        // Al cargar la página
        document.addEventListener("DOMContentLoaded", function() {{
            // Bloquear mapa inicialmente
            map.getContainer().style.pointerEvents = "none";
            
            // Ocultar buscador inicialmente
            if (document.getElementById("lupitaBuscador")) {{
                document.getElementById("lupitaBuscador").style.display = "none";
            }}
            
            // Ocultar botón de gráficos inicialmente
            if (document.getElementById("btnGraficos")) {{
                document.getElementById("btnGraficos").style.display = "none";
            }}
            
            // Verificar si ya tiene sesión activa
            if (!verificarSesionActiva()) {{
                // Enfocar usuario input
                setTimeout(() => {{
                    document.getElementById("loginUsuario").focus();
                }}, 500);
            }}
        }});
        </script>
        '''
        
        m.get_root().html.add_child(folium.Element(login_html))
        
        # 💾 GUARDAR ARCHIVO HTML
        from datetime import datetime
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M")
        output_file = f"visor_cultivos_automatico_{fecha_str}.html"
        m.save(output_file)
        
        print(f"\n✅ Aplicación guardada como: {output_file}")
        print(f"🔐 Credenciales para la aplicación web:")
        print(f"   Usuario: {USUARIO_CORRECTO}")
        print(f"   Contraseña: {CONTRASENA_CORRECTA}")
        
        # 📊 MOSTRAR COMPARACIÓN POR ZONA EN CONSOLA
        print(f"\n📊 COMPARACIÓN PROYECTADO vs REAL POR ZONA:")
        print(f"{'ZONA':<8} {'PROYECTADO':>15} {'REAL':>15} {'DIFERENCIA':>15} {'%':>10}")
        print(f"{'-'*8} {'-'*15} {'-'*15} {'-'*15} {'-'*10}")
        
        for zona in zonas_ordenadas:
            proyectado = hectareas_proyectadas.get(zona, 0)
            real = hectareas_por_zona.get(zona, 0) if zona in hectareas_por_zona else 0
            diferencia = real - proyectado
            porcentaje = (diferencia / proyectado * 100) if proyectado > 0 else 0
            
            color_icono = "🟢" if diferencia >= 0 else "🔴"
            signo = "+" if diferencia >= 0 else ""
            
            print(f"Zona {zona:<4} {proyectado:>15,.0f} {real:>15,.0f} {signo}{diferencia:>14,.0f} {porcentaje:>9.1f}% {color_icono}")
        
        total_proyectado = sum(hectareas_proyectadas.values())
        total_real = sum(hectareas_por_zona.values())
        total_diferencia = total_real - total_proyectado
        total_porcentaje = (total_diferencia / total_proyectado * 100) if total_proyectado > 0 else 0
        
        print(f"{'='*8} {'='*15} {'='*15} {'='*15} {'='*10}")
        print(f"{'TOTAL':<8} {total_proyectado:>15,.0f} {total_real:>15,.0f} {total_diferencia:>+15,.0f} {total_porcentaje:>9.1f}%")
        
        print(f"\n📋 INSTRUCCIONES:")
        print(f"   1. 📂 El archivo HTML se ha generado automáticamente")
        print(f"   2. 🌐 Puedes abrir '{output_file}' en cualquier navegador")
        print(f"   3. 🔐 Usa las credenciales para acceder a la aplicación")
        print(f"   4. 🔍 Buscador disponible después del login")
        print(f"   5. 📊 Panel de comparación por zona disponible")
        print(f"\n✅ Proceso completado exitosamente!")
        
    except Exception as e:
        print(f"❌ Error al crear la aplicación: {str(e)}")
        import traceback
        traceback.print_exc()

# --- EJECUTAR LA APLICACIÓN AUTOMÁTICAMENTE ---
if __name__ == "__main__":
    crear_app_geojson()
