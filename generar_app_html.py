#!/usr/bin/env python3
"""
GENERADOR AUTOMÁTICO DE APLICACIÓN HTML IDÉNTICO A COLAB
Versión para GitHub Actions - EXACTA A LA VERSIÓN DE COLAB
Con TODO el JavaScript original preservado
"""

import geopandas as gpd
import pandas as pd
import json
import folium
from folium import GeoJson
from folium.plugins import Fullscreen, MeasureControl, LocateControl
import hashlib
import sys
import os
from datetime import datetime
from owslib.wms import WebMapService
import re

print("🔐🌽🌱 GENERADOR DE APLICACIÓN WEB COMPLETA - PROGRAMA CÓRDOBA 25/26")
print("=" * 80)

# 🔐 CREDENCIALES DE ACCESO (MISMO QUE EN COLAB)
USUARIO_CORRECTO = os.environ.get("MULTIRIESGO_USER")
CONTRASENA_CORRECTA = os.environ.get("MULTIRIESGO_PASS")

# Verificar que se cargaron las credenciales
if not USUARIO_CORRECTO or not CONTRASENA_CORRECTA:
    print("⚠️  ADVERTENCIA: No se encontraron credenciales en variables de entorno")
    print("   Usando valores por defecto (solo para desarrollo)")
    USUARIO_CORRECTO = USUARIO_CORRECTO or "UsuarioDemo"
    CONTRASENA_CORRECTA = CONTRASENA_CORRECTA or "PassDemo"

def generar_hash_seguro(texto):
    """Genera hash SHA-256 con salt para mayor seguridad"""
    salt = "ProgramaCordoba25/26-SancorSeguro"
    hash_obj = hashlib.sha256(f"{texto}{salt}".encode())
    return hash_obj.hexdigest()[:16]

HASH_USUARIO = generar_hash_seguro(USUARIO_CORRECTO)
HASH_CONTRASENA = generar_hash_seguro(CONTRASENA_CORRECTA)

def cargar_geojson(ruta_geojson):
    """Carga un archivo GeoJSON"""
    print(f"📖 Cargando {ruta_geojson}...")
    with open(ruta_geojson, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
    gdf.crs = "EPSG:4326"
    
    print(f"✅ GeoJSON cargado: {len(gdf)} polígonos")
    return geojson_data, gdf

def encontrar_campos(gdf):
    """Encuentra campos clave automáticamente (IDÉNTICO A COLAB)"""
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

    campo_causa_stro = None
    for campo in ['CAUSA_STRO', 'CAUSA_SINIESTRO', 'CAUSA', 'causa_stro']:
        if campo in gdf.columns:
            campo_causa_stro = campo
            break

    campo_fecha_stro = None
    # Buscar EXACTAMENTE como en Colab
    if 'Fecha Stro' in gdf.columns:
        campo_fecha_stro = 'Fecha Stro'
    else:
        for campo in ['FechaStro', 'Fecha_Stro', 'FECHA_STRO', 'FECHA_SINIESTRO', 'FECHA', 'fecha_stro']:
            if campo in gdf.columns:
                campo_fecha_stro = campo
                break

    campo_dano_stro = None
    for campo in ['DAÑO_ESTIMADO', 'DAÑO', 'DANO_ESTIMADO', 'DANO', 'PERDIDA', 'PERDIDA_ESTIMADA']:
        if campo in gdf.columns:
            campo_dano_stro = campo
            break

    return {
        'cultivo': campo_cultivo,
        'hectareas': campo_hectareas,
        'cliente': campo_cliente,
        'zona': campo_zona,
        'causa_stro': campo_causa_stro,
        'fecha_stro': campo_fecha_stro,
        'dano_stro': campo_dano_stro
    }

def agregar_elemento_html_seguro(mapa, html_content):
    """Agrega HTML de forma segura usando branca.element.Element"""
    try:
        from branca.element import Element
        element = Element(html_content)
        mapa.get_root().html.add_child(element)
        return True
    except Exception as e:
        print(f"⚠️  Error agregando HTML (branca): {e}")
        try:
            # Intento alternativo
            mapa.get_root().html.add_child(folium.Element(html_content))
            return True
        except Exception as e2:
            print(f"❌ Error crítico: {e2}")
            return False

def crear_app_completa(geojson_data, gdf, campos, output_file):
    """CREA LA APLICACIÓN 100% IDÉNTICA A COLAB - VERSIÓN CORREGIDA"""
    
    print(f"\n🗺️ Creando aplicación web 100% IDÉNTICA A COLAB: {output_file}")
    
    # Centro del mapa (IDÉNTICO)
    if not gdf.empty:
        minx, miny, maxx, maxy = gdf.total_bounds
        bounds = [[miny, minx], [maxy, maxx]]
        center = [(miny + maxy) / 2, (minx + maxx) / 2]
    else:
        center = [-31.4201, -64.1888]
        bounds = [[center[0]-0.1, center[1]-0.1], [center[0]+0.1, center[1]+0.1]]

    # Crear mapa base
    m = folium.Map(
        location=center,
        zoom_start=11,
        control_scale=True,
        tiles=None,
        zoom_control=True
    )

    # ========== CAPAS BASE (ACTUALIZADAS - ESRI) ==========
    # Esri Satélite
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='🛰️ Esri Satélite',
        max_zoom=19,
        overlay=False,
        control=True
    ).add_to(m)

    # Google Híbrido (se mantiene)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google',
        name='🗺️ Google Híbrido',
        max_zoom=20,
        overlay=False,
        control=True
    ).add_to(m)

    # Esri Dark Gray
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='🌙 Esri Dark Gray',
        max_zoom=16,
        overlay=False,
        control=True
    ).add_to(m)

    # Esri Standard
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='🗺️ Esri Standard',
        max_zoom=19,
        overlay=False,
        control=True
    ).add_to(m)

    # ========== ESTILOS POR CULTIVO (100% IDÉNTICOS) ==========
    def estilo_por_cultivo(feature):
        propiedades = feature['properties']

        color_relleno = '#9C27B0'
        color_borde = '#7B1FA2'

        if campos['cultivo'] and campos['cultivo'] in propiedades:
            cultivo = str(propiedades[campos['cultivo']]).lower()

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

    # ========== ESTILOS PARA SINIESTROS (100% IDÉNTICOS) ==========
    def estilo_por_causa_siniestro(feature):
        """Estilo específico para siniestros - IDÉNTICO A COLAB"""
        propiedades = feature['properties']
        causa = propiedades.get(campos['causa_stro'], '').upper() if campos['causa_stro'] else ''

        # Mapeo de colores por causa de siniestro (EXACTO)
        colores_causa = {
            'GRANIZO': ('#00BCD4', '#0097A7'),
            'SEQUÍA': ('#FF5252', '#D50000'),
            'SEQUIA': ('#FF5252', '#D50000'),
            'INUNDACIÓN': ('#448AFF', '#2979FF'),
            'INUNDACION': ('#448AFF', '#2979FF'),
            'VIENTO': ('#7C4DFF', '#651FFF'),
            'INCENDIO': ('#795548', '#5D4037'),
            'HELADA': ('#FFFFFF', '#E0E0E0'),
        }
        
        if causa in colores_causa:
            fill_color, border_color = colores_causa[causa]
        else:
            fill_color, border_color = '#9C27B0', '#7B1FA2'

        # Guardar colores en propiedades
        feature['properties']['_color_fill_siniestro'] = fill_color
        feature['properties']['_color_border_siniestro'] = border_color

        return {
            'fillColor': fill_color,
            'color': border_color,
            'weight': 3,
            'fillOpacity': 0.7,
            'dashArray': '3, 3'
        }

    def highlight_function_siniestros(feature):
        """Resaltado específico para siniestros"""
        return {
            'fillColor': '#FF5722',
            'color': '#D84315',
            'weight': 4,
            'fillOpacity': 0.9,
            'dashArray': '3, 3'
        }

    # ========== CAMPOS PARA POPUP (100% IDÉNTICOS) ==========
    campos_especificos = [
        'CUIT', 'CLIENTE', 'CAMPO', 'DEPARTAMENTO', 'LOCALIDAD', 'CULTIVO', 'LOTE',
        'CULTIVO_ANTERIOR', 'RENDIMIENTO_ANTERIOR', 'HECTAREAS_DECLARADAS',
        'HECTAREAS_ASEGURADAS', 'PORCENTAJE_ASEGURADO', 'ZONA_CZ4',
        'RENDIMIENTO_ASEGURADO', 'SUMA_ASEGURADA', 'FECHA_SIEMBRA'
    ]

    campos_existentes = [campo for campo in campos_especificos if campo in gdf.columns]
    campos_numericos = [col for col in gdf.columns if pd.api.types.is_numeric_dtype(gdf[col])]
    otros_campos = [campo for campo in campos_numericos if campo not in campos_existentes and 'HECTAREAS' in campo]
    campos_para_popup = campos_existentes + otros_campos[:5]

    campos_tooltip = []
    if campos['cliente'] and campos['cliente'] in gdf.columns:
        campos_tooltip = [campos['cliente']]
    elif campos['cultivo'] and campos['cultivo'] in gdf.columns:
        campos_tooltip = [campos['cultivo']]
    else:
        campos_tooltip = ['excel_fila_num']

    # ========== CAPA PRINCIPAL (100% IDÉNTICA) ==========
    geo_layer = folium.GeoJson(
        geojson_data,
        name='Lotes asegurados',
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

    # ========== CAPA DE FOTOS DESDE GITHUB (100% IDÉNTICA) ==========
    print("📸 Configurando capa de fotos desde GitHub (VERSIÓN EXACTA COLAB)...")
    
    # URL del archivo de fotos en GitHub
    GITHUB_USER = "franciscotomatis"
    REPO_NAME = "APP-C-rdoba"
    FOTOS_JSON_URL = "https://raw.githubusercontent.com/franciscotomatis/APP-C-rdoba/main/fotos_metadata/fotos_procesadas.json"

    print(f"✅ Fotos se cargarán desde: {FOTOS_JSON_URL}")

    # ========== HTML Y JAVASCRIPT DE FOTOS - VERSIÓN EXACTA DE COLAB ==========
    fotos_html = f'''
    <div id="contenedorFotosGithub">
        <!-- Indicador de carga -->
        <div id="cargandoFotos" style="position: fixed;
                top: 120px; right: 20px;
                background: rgba(244, 67, 54, 0.9);
                color: white;
                padding: 8px 12px;
                border-radius: 8px;
                z-index: 10000;
                font-family: Arial, sans-serif;
                font-size: 11px;
                display: none;
                box-shadow: 0 3px 10px rgba(244, 67, 54, 0.3);
                border: 1px solid #D32F2F;
                min-width: 160px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="width: 24px; height: 24px; background: rgba(255, 255, 255, 0.3); 
                        border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                    <span style="font-size: 12px; animation: spin 1s linear infinite;">⏳</span>
                </div>
                <div>
                    <div style="font-weight: bold; font-size: 12px;">Cargando fotos...</div>
                </div>
            </div>
        </div>
    </div>

    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>

    <script>
    // Variables globales - TODO IGUAL
    var capaFotosGithub = null;
    var fotosCargadas = false;
    var cargandoFotos = false;
    var capaVisible = false;

    // Función para crear popup de foto - VERSIÓN EXACTA
    function crearPopupFotoGithub(feature) {{
        var props = feature.properties || {{}};
        var nombre = props.NOMBRE_FOTO || "Foto del perito";
        var metodo = props.METODO || "Desconocido";
        var imgUrl = props.IMAGEN_URL || props.IMAGEN || "";
        
        var html = `
        <div style="font-family: Arial, sans-serif; max-width: 500px; min-width: 300px;">
            <div style="background: linear-gradient(135deg, #F44336, #D32F2F); 
                        color: white; padding: 12px; border-radius: 8px 8px 0 0;
                        text-align: center;">
                <div style="font-size: 14px; font-weight: bold;">📸 ${{nombre}}</div>
                <div style="font-size: 10px; opacity: 0.9; margin-top: 3px;">${{metodo}}</div>
            </div>
            
            <div style="padding: 15px; text-align: center; background: #FFF3F2;">
                <img src="${{imgUrl}}" 
                    style="max-width: 100%; max-height: 350px; 
                            border-radius: 6px; border: 2px solid #F44336;
                            box-shadow: 0 3px 10px rgba(0,0,0,0.15);
                            cursor: pointer;"
                    onclick="this.style.maxHeight='none'; this.style.cursor='default';"
                    title="Click para ampliar la foto">
            </div>
            
            <div style="padding: 8px; background: #f9f9f9; border-radius: 0 0 8px 8px;
                        border-top: 1px solid #eee; font-size: 10px; color: #666;">
                <div style="text-align: center;">
                    📍 Foto geolocalizada • 👤 Perito en campo
                </div>
                <div style="margin-top: 5px; text-align: center; font-size: 9px;">
                    Click en la foto para ampliar • Programa Córdoba 25/26
                </div>
            </div>
        </div>
        `;
        
        return L.popup({{
            maxWidth: 550,
            minWidth: 320
        }}).setContent(html);
    }}

    // Función principal para cargar fotos - EXACTAMENTE IGUAL QUE COLAB
    async function cargarFotosDesdeGithub() {{
        if (fotosCargadas || cargandoFotos) return;
        
        cargandoFotos = true;
        var cargandoDiv = document.getElementById("cargandoFotos");
        if (cargandoDiv) cargandoDiv.style.display = "block";
        
        console.log("📸 Cargando fotos desde GitHub...");
        
        try {{
            // 1. Hacer fetch al archivo de fotos
            const response = await fetch("{FOTOS_JSON_URL}");
            
            if (!response.ok) {{
                throw new Error(`Error HTTP: ${{response.status}}`);
            }}
            
            // 2. Parsear el JSON
            const fotosData = await response.json();
            const features = fotosData.features || [];
            
            console.log(`✅ ${{features.length}} fotos cargadas`);
            
            // 3. Crear capa de fotos - EXACTO
            capaFotosGithub = L.geoJSON(features, {{
                pointToLayer: function(feature, latlng) {{
                    // Crear marcador circular ROJO con borde BLANCO
                    var marker = L.circleMarker(latlng, {{
                        radius: 8,
                        fillColor: "#F44336",      // ROJO
                        color: "#FFFFFF",          // BLANCO (borde)
                        weight: 2,                // Grosor del borde
                        opacity: 1,
                        fillOpacity: 0.9
                    }});
                    
                    // Forzar que cada marcador esté arriba
                    marker.options.zIndexOffset = 1000;
                    return marker;
                }},
                
                onEachFeature: function(feature, layer) {{
                    // Agregar tooltip simple
                    var nombre = feature.properties.NOMBRE_FOTO || "Foto";
                    layer.bindTooltip(`📸 ${{nombre}}`, {{
                        sticky: true,
                        direction: 'top',
                        className: 'foto-tooltip',
                        opacity: 0.9
                    }});
                    
                    // Agregar popup con imagen
                    layer.bindPopup(crearPopupFotoGithub(feature));
                }}
            }});
            
            // 4. Agregar capa al mapa - VERSIÓN EXACTA
            function agregarCapaAlMapa() {{
                console.log("🔍 Buscando mapa...");
                
                var mapaActual = null;
                
                // Buscar window.map primero
                if (typeof window.map !== "undefined" && window.map !== null) {{
                    mapaActual = window.map;
                    console.log("✅ Mapa encontrado: window.map");
                }}
                // Buscar cualquier objeto Leaflet
                else {{
                    for (var key in window) {{
                        try {{
                            var obj = window[key];
                            if (obj && 
                                typeof obj.addLayer === "function" && 
                                typeof obj.fitBounds === "function") {{
                                mapaActual = obj;
                                console.log("✅ Mapa encontrado: window." + key);
                                break;
                            }}
                        }} catch(e) {{
                            // Ignorar errores
                        }}
                    }}
                }}
                
                if (mapaActual && typeof mapaActual.addLayer === "function") {{
                    try {{
                        mapaActual.addLayer(capaFotosGithub);
                        console.log("✅ Capa de fotos agregada");
                        fotosCargadas = true;
                        capaVisible = true;
                        
                        // ========== CLAVE ==========
                        // Forzar que esté arriba de todo
                        capaFotosGithub.bringToFront();
                        // ===========================
                        
                        return true;
                    }} catch (error) {{
                        console.error("❌ Error:", error);
                        return false;
                    }}
                }} else {{
                    console.warn("⚠️ Reintentando...");
                    setTimeout(agregarCapaAlMapa, 500);
                    return false;
                }}
            }}

            // Llamar a la función
            agregarCapaAlMapa();
            
        }} catch (error) {{
            console.error("❌ Error cargando fotos:", error);
            
            // Mostrar error breve
            var cargandoDiv = document.getElementById("cargandoFotos");
            if (cargandoDiv) {{
                cargandoDiv.innerHTML = `
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 24px; height: 24px; background: rgba(255, 0, 0, 0.2); 
                            border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                        <span style="font-size: 12px; color: #FF0000;">❌</span>
                    </div>
                    <div style="font-size: 11px;">Error cargando fotos</div>
                </div>
                `;
            }}
            
        }} finally {{
            cargandoFotos = false;
            // Ocultar mensaje después de 2 segundos
            setTimeout(function() {{
                var cargandoDiv = document.getElementById("cargandoFotos");
                if (cargandoDiv) cargandoDiv.style.display = "none";
            }}, 2000);
        }}
    }}

    // FUNCIÓN TOGGLE - Con bringToFront cuando se muestran
    function toggleFotos(mostrar) {{
        if (!capaFotosGithub) return;
        
        capaVisible = mostrar;
        
        if (mostrar) {{
            // Mostrar y traer al frente
            capaFotosGithub.setStyle({{
                opacity: 1,
                fillOpacity: 0.9
            }});
            capaFotosGithub.bringToFront(); // <-- EXACTO
            console.log("✅ Fotos mostradas (ARRIBA)");
        }} else {{
            // Ocultar
            capaFotosGithub.setStyle({{
                opacity: 0,
                fillOpacity: 0
            }});
            console.log("✅ Fotos ocultadas");
        }}
    }}

    // Detección del checkbox - EXACTAMENTE IGUAL
    function configurarDeteccionFotos() {{
        function buscarCheckbox() {{
            var checkboxes = document.querySelectorAll('input[type="checkbox"]');
            
            for (var i = 0; i < checkboxes.length; i++) {{
                var checkbox = checkboxes[i];
                var label = checkbox.parentElement;
                
                if (label && label.textContent && label.textContent.includes("📸 Fotos del perito")) {{
                    console.log("✅ Checkbox de fotos encontrado");
                    
                    checkbox.addEventListener("change", function() {{
                        console.log("🔄 Checkbox cambiado:", this.checked);
                        
                        if (this.checked) {{
                            if (!fotosCargadas) {{
                                cargarFotosDesdeGithub();
                            }} else {{
                                toggleFotos(true);
                            }}
                        }} else {{
                            toggleFotos(false);
                        }}
                    }});
                    
                    return true;
                }}
            }}
            
            return false;
        }}
        
        var intentos = 0;
        function intentarBuscar() {{
            if (buscarCheckbox()) {{
                console.log("✅ Sistema de fotos configurado");
            }} else {{
                intentos++;
                if (intentos < 5) {{
                    setTimeout(intentarBuscar, 1000);
                }} else {{
                    console.warn("⚠️ No se encontró el checkbox de fotos");
                }}
            }}
        }}
        
        intentarBuscar();
    }}

    // Inicializar cuando cargue la página
    document.addEventListener("DOMContentLoaded", configurarDeteccionFotos);
    
    // También escuchar si el mapa se carga después
    if (typeof window.map !== "undefined") {{
        window.map.whenReady(configurarDeteccionFotos);
    }}
    </script>
    '''

    # Crear capa vacía para fotos (igual que en Colab)
    fotos_layer = folium.FeatureGroup(name='📸 Fotos del perito', show=True)
    fotos_layer.add_to(m)

    # Agregar el HTML/JavaScript al mapa
    agregar_elemento_html_seguro(m, fotos_html)

    print("✅ Sistema de carga de fotos desde GitHub configurado (VERSIÓN EXACTA)")

    # ========== CAPA DE SINIESTROS (100% IDÉNTICA) ==========
    if campos['causa_stro'] and gdf[campos['causa_stro']].notna().any():
        print("✅ Encontrados datos de siniestros")
        
        # Filtrar solo los polígonos que tienen causa de siniestro
        siniestros_features = []
        for feature in geojson_data['features']:
            if feature['properties'].get(campos['causa_stro']):
                siniestros_features.append(feature)

        if siniestros_features:
            siniestros_data = {
                "type": "FeatureCollection",
                "features": siniestros_features
            }

            print(f"✅ {len(siniestros_features)} polígonos con siniestros")

            # Campos para siniestros (EXACTAMENTE como en Colab)
            campos_siniestros_popup = [campos['causa_stro']]
            aliases_siniestros = ['<b>Causa del siniestro</b>']
            
            if campos['fecha_stro']:
                campos_siniestros_popup.append(campos['fecha_stro'])
                aliases_siniestros.append('<b>Fecha del siniestro</b>')
                
            if campos['dano_stro']:
                campos_siniestros_popup.append(campos['dano_stro'])
                aliases_siniestros.append('<b>Daño estimado</b>')
            
            # Agregar campos generales
            campos_siniestros_popup.extend(campos_para_popup[:5])
            aliases_siniestros.extend([f"<b>{col}</b>" for col in campos_para_popup[:5]])

            # Crear capa de siniestros SEPARADA (EXACTO)
            siniestros_layer = folium.GeoJson(
                siniestros_data,
                name='⚠️ Siniestros',
                style_function=estilo_por_causa_siniestro,
                highlight_function=highlight_function_siniestros,
                tooltip=folium.GeoJsonTooltip(
                    fields=[campos['causa_stro']] + campos_tooltip[:3],
                    aliases=['Causa'] + [f"{campo}" for campo in campos_tooltip[:3]],
                    localize=True,
                    sticky=True,
                    style="""
                        font-family: Arial, sans-serif;
                        font-size: 11px;
                        background-color: rgba(255, 255, 255, 0.95);
                        border: 2px solid #F44336;
                        border-radius: 3px;
                        padding: 5px;
                    """
                ),
                popup=folium.GeoJsonPopup(
                    fields=campos_siniestros_popup,
                    aliases=aliases_siniestros,
                    localize=True,
                    labels=True,
                    style="""
                        font-family: Arial, sans-serif;
                        font-size: 11px;
                        max-height: 400px;
                        overflow-y: auto;
                        max-width: 350px;
                        padding: 10px;
                        background-color: #ffebee;
                        border: 2px solid #F44336;
                        border-radius: 5px;
                    """
                ),
                show=False  # IMPORTANTE: Ocultar por defecto
            ).add_to(m)

            # Obtener el nombre de la capa de siniestros para JavaScript
            capa_siniestros_nombre = siniestros_layer.get_name()

            # Obtener causas únicas
            causas_unicas = sorted(gdf[campos['causa_stro']].dropna().unique())

            # ========== BUSCADOR PARA SINIESTROS (100% IDÉNTICO) ==========
            opciones_causas = "".join(f'<option value="{causa}">{causa}</option>' for causa in causas_unicas)
            
            buscador_siniestros_html = f'''
            <div id="buscadorSiniestros" style="position: fixed;
                    top: 260px; left: 10px;
                    background-color: rgba(244, 67, 54, 0.95);
                    padding: 8px 10px;
                    border-radius: 6px;
                    border: 2px solid #C62828;
                    z-index: 9997;
                    font-family: Arial, sans-serif;
                    font-size: 11px;
                    width: 220px;
                    box-shadow: 0 3px 8px rgba(0,0,0,0.15);
                    display: none;">

                <!-- CABECERA -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="font-weight: bold; color: white; font-size: 12px; display: flex; align-items: center;">
                        <span style="margin-right: 5px;">⚠️</span>
                        Filtrar siniestros
                    </div>
                    <button onclick="toggleBuscadorSiniestros()"
                            style="background: none; border: none; cursor: pointer; font-size: 14px; color: white;">
                            ×</button>
                </div>

                <!-- CONTENIDO -->
                <div id="contenidoBuscadorSiniestros">
                    <div style="margin-bottom: 8px;">
                        <select id="causaSiniestroSelect"
                               style="width: 100%; padding: 5px; border: 1px solid #ddd;
                                      border-radius: 3px; font-size: 11px;">
                            <option value="">Todas las causas</option>
                            {opciones_causas}
                        </select>
                    </div>

                    <div style="display: flex; gap: 5px; margin-bottom: 6px;">
                        <button onclick="filtrarSiniestros()"
                                style="flex: 1; background-color: white; color: #F44336;
                                       border: none; padding: 5px; border-radius: 3px;
                                       cursor: pointer; font-size: 10px; font-weight: bold;">
                            Filtrar
                        </button>
                        <button onclick="mostrarTodosSiniestros()"
                                style="flex: 1; background-color: #FFCCBC; color: #D84315;
                                       border: none; padding: 5px; border-radius: 3px;
                                       cursor: pointer; font-size: 10px;">
                            Mostrar todos
                        </button>
                    </div>

                    <div id="estadoSiniestros"
                         style="font-size: 9px; color: white; margin-top: 6px;
                                padding-top: 5px; border-top: 1px solid rgba(255,255,255,0.3);">
                        Total: {len(siniestros_features)} siniestros
                    </div>
                </div>
            </div>

            <script>
            // Variable para controlar visibilidad del buscador
            var buscadorSiniestrosVisible = false;

            function toggleBuscadorSiniestros() {{
                var buscador = document.getElementById("buscadorSiniestros");
                if (buscadorSiniestrosVisible) {{
                    buscador.style.display = "none";
                }} else {{
                    buscador.style.display = "block";
                }}
                buscadorSiniestrosVisible = !buscadorSiniestrosVisible;
            }}

            // Mostrar buscador cuando se activa la capa de siniestros
            function onCapaSiniestrosChange() {{
                var checkbox = document.querySelector('input[title="⚠️ Siniestros"]');
                var buscador = document.getElementById("buscadorSiniestros");

                if (checkbox && checkbox.checked) {{
                    buscador.style.display = "block";
                    buscadorSiniestrosVisible = true;
                }} else {{
                    buscador.style.display = "none";
                    buscadorSiniestrosVisible = false;
                }}
            }}

            // Función para filtrar siniestros
            function filtrarSiniestros() {{
                var causaSeleccionada = document.getElementById("causaSiniestroSelect").value;
                var capaSiniestros = {capa_siniestros_nombre};
                var contador = 0;

                capaSiniestros.eachLayer(function(layer) {{
                    var causa = layer.feature.properties.{campos['causa_stro']} || '';

                    if (!causaSeleccionada || causa === causaSeleccionada) {{
                        // Mostrar este polígono
                        layer.setStyle({{
                            fillOpacity: 0.7,
                            weight: 3,
                            opacity: 1
                        }});
                        layer.options.interactive = true;
                        contador++;
                    }} else {{
                        // OCULTAR COMPLETAMENTE este polígono
                        layer.setStyle({{
                            fillOpacity: 0,
                            weight: 0,
                            opacity: 0
                        }});
                        
                        // DESHABILITAR INTERACTIVIDAD TOTALMENTE
                        layer.options.interactive = false;
                        
                        // Remover tooltip si existe
                        if (layer._tooltip) {{
                            layer.unbindTooltip();
                        }}
                        
                        // Remover popup si existe  
                        if (layer._popup) {{
                            layer.unbindPopup();
                        }}
                        
                        // Remover eventos de mouse
                        layer.off('mouseover');
                        layer.off('mouseout');
                        layer.off('click');
                        
                        // Hacer que el layer no responda a ningún evento
                        layer.options.bubblingMouseEvents = false;
                    }}
                }});

                document.getElementById("estadoSiniestros").innerHTML =
                    "Mostrando: " + contador + " siniestros" +
                    (causaSeleccionada ? " (" + causaSeleccionada + ")" : "");
            }}

            function mostrarTodosSiniestros() {{
                document.getElementById("causaSiniestroSelect").value = "";
                filtrarSiniestros();
            }}

            // Detectar cambios en el checkbox de siniestros
            document.addEventListener("DOMContentLoaded", function() {{
                setTimeout(function() {{
                    // Escuchar cambios en el checkbox de siniestros
                    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
                    checkboxes.forEach(function(checkbox) {{
                        if (checkbox.parentElement && checkbox.parentElement.textContent.includes('⚠️ Siniestros')) {{
                            checkbox.addEventListener("change", onCapaSiniestrosChange);
                        }}
                    }});

                    // Inicializar
                    onCapaSiniestrosChange();
                }}, 1000);
            }});

            // Permitir usar Enter en el select
            document.getElementById("causaSiniestroSelect").addEventListener("keypress", function(e) {{
                if (e.key === "Enter") {{
                    filtrarSiniestros();
                }}
            }});
            </script>
            '''

            agregar_elemento_html_seguro(m, buscador_siniestros_html)

    # ========== CAPAS WMS (100% IDÉNTICAS) ==========
    print("\n" + "="*60)
    print("📡 AGREGANDO CAPAS WMS (IDÉNTICAS A COLAB)")
    print("="*60)

    # IMERG DIARIO
    try:
        url_wms = "https://geoservicios2.conae.gov.ar/geoserver/PrecipitacionAcumulada/wms"
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
                
    except Exception as e:
        print(f"⚠️ Error IMERG: {e}")

    # HUMEDAD DE SUELO
    try:
        print("\n💧 Agregando capa de Humedad de Suelo CONAE...")
        
        url_wms = "https://geoservicios3.conae.gov.ar/geoserver/HumedadDeSuelos/wms"
        nombre_capa = "HumedadDeSuelos:DSS_MSMKR_1"
        nombre_display = "💧 Humedad Suelo (primeros 50 cm)"
        
        folium.WmsTileLayer(
            url=url_wms,
            name=nombre_display,
            layers=nombre_capa,
            fmt='image/png',
            transparent=True,
            opacity=0.65,
            overlay=True,
            control=True,
            show=False
        ).add_to(m)
        
        print(f"✅ {nombre_display} agregada")
        
    except Exception as e:
        print(f"⚠️ Error Humedad Suelo: {e}")

    # TVDI MODIS
    try:
        url_wms = "https://aplicaciones.gulich.unc.edu.ar/geoserver/ows"
        wms = WebMapService(url_wms, version='1.3.0')
        
        config_capas = [
            {
                "nombre": "tvdi_m_2024:tvdi_2026009_modis",
                "simbolo": "📊",
                "nombre_display": "TVDI",
                "opacidad": 0.75
            },
            {
                "nombre": "tvdi_anomsindex_m_2024:anomtvdi_2026009_anomindex_modis",
                "simbolo": "🟡", 
                "nombre_display": "Anomalía TVDI",
                "opacidad": 0.75
            }
        ]
        
        for config in config_capas:
            nombre_capa = config["nombre"]
            simbolo = config["simbolo"]
            nombre_base = config["nombre_display"]
            
            if nombre_capa in wms.contents:
                match = re.search(r'(\d{4})(\d{3})', nombre_capa)
                
                if match:
                    año = match.group(1)
                    dia_año = int(match.group(2))
                    nombre_mostrar = f"{simbolo} {nombre_base} {año}-Día{dia_año}"
                else:
                    nombre_mostrar = f"{simbolo} {nombre_base}"
                
                folium.WmsTileLayer(
                    url=url_wms,
                    name=nombre_mostrar,
                    layers=nombre_capa,
                    fmt='image/png',
                    transparent=True,
                    opacity=config["opacidad"],
                    overlay=True,
                    control=True,
                    show=False,
                    styles='',
                    version='1.3.0'
                ).add_to(m)
                
                print(f"✅ {nombre_mostrar}")
                
    except Exception as e:
        print(f"⚠️ Error TVDI: {e}")

    # ========== LEYENDAS WMS (100% IDÉNTICAS) ==========
    
    # URLs de leyendas
    url_leyenda_normal = "https://aplicaciones.gulich.unc.edu.ar/geoserver/ows?service=WMS&version=1.3.0&request=GetLegendGraphic&format=image/png&layer=tvdi_m_2024:tvdi_2025361_modis&style=tvdi61"
    url_leyenda_anomalia = "https://aplicaciones.gulich.unc.edu.ar/geoserver/ows?service=WMS&version=1.3.0&request=GetLegendGraphic&format=image/png&layer=tvdi_anomsindex_m_2024:anomtvdi_2025361_anomindex_modis&style=anomaliasTVDIindex"
    url_leyenda_imerg = "https://geoservicios2.conae.gov.ar/geoserver/PrecipitacionAcumulada/wms?service=WMS&version=1.3.0&request=GetLegendGraphic&format=image/png&layer=MOM_GPMIMERG_PA1D_1&style=estilo_MOM_CMORPH2_PA1D"
    
    # LEYENDA NORMAL TVDI
    leyenda_normal_html = f'''
    <div id="leyendaNormal" style="position: fixed;
            bottom: 120px; left: 10px;
            background-color: white;
            padding: 8px;
            border-radius: 6px;
            border: 2px solid #9C27B0;
            z-index: 9996;
            width: 160px;
            display: none;
            box-shadow: 0 4px 15px rgba(0,0,0,0.25);">

        <div style="display: flex; justify-content: space-between; 
                    align-items: center; margin-bottom: 8px; padding-bottom: 6px;
                    border-bottom: 1px solid #e0e0e0;">
            <div style="font-size: 11px; font-weight: bold; color: #9C27B0;">
                📊 TVDI
            </div>
            <button onclick="ocultarLeyendaTvdi('normal')"
                    style="background: none; border: none; color: #666;
                           font-size: 16px; cursor: pointer; padding: 0;
                           line-height: 1; width: 20px; height: 20px;
                           display: flex; align-items: center; justify-content: center;
                           border-radius: 2px;"
                    title="Cerrar leyenda">
                ×
            </button>
        </div>

        <div style="text-align: center; background-color: white; padding: 5px; border-radius: 4px;">
            <img src="{url_leyenda_normal}" 
                 alt="Leyenda TVDI Normal"
                 style="max-width: 100%; 
                        height: auto;
                        border-radius: 3px;
                        display: block;">
        </div>
    </div>

    <div id="btnLeyendaNormal" style="position: fixed;
            bottom: 85px; left: 10px;
            background-color: #9C27B0;
            color: white;
            padding: 6px 10px;
            border-radius: 5px;
            z-index: 9996;
            cursor: pointer;
            font-family: Arial, sans-serif;
            font-size: 10px;
            display: none;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            align-items: center;
            gap: 5px;
            border: 1px solid #7B1FA2;"
            onclick="mostrarLeyendaTvdi('normal')"
            title="Mostrar leyenda TVDI Normal"
            onmouseover="this.style.backgroundColor='#7B1FA2'; this.style.transform='translateY(-1px)';"
            onmouseout="this.style.backgroundColor='#9C27B0'; this.style.transform='translateY(0)';">
        <span style="font-size: 12px;">📊</span>
        <span style="color: white;">Leyenda</span>
    </div>
    '''
    
    # LEYENDA ANOMALÍA TVDI
    leyenda_anomalia_html = f'''
    <div id="leyendaAnomalia" style="position: fixed;
            bottom: 120px; left: 10px;
            background-color: white;
            padding: 8px;
            border-radius: 6px;
            border: 2px solid #FF9800;
            z-index: 9996;
            width: 160px;
            display: none;
            box-shadow: 0 4px 15px rgba(0,0,0,0.25);">
        
        <div style="display: flex; justify-content: space-between; 
                    align-items: center; margin-bottom: 8px; padding-bottom: 6px;
                    border-bottom: 1px solid #e0e0e0;">
            <div style="font-size: 11px; font-weight: bold; color: #FF9800;">
                🟡 Anomalía
            </div>
            <button onclick="ocultarLeyendaTvdi('anomalia')"
                    style="background: none; border: none; color: #666;
                           font-size: 16px; cursor: pointer; padding: 0;
                           line-height: 1; width: 20px; height: 20px;
                           display: flex; align-items: center; justify-content: center;
                           border-radius: 2px;"
                    title="Cerrar leyenda">
                ×
            </button>
        </div>

        <div style="text-align: center; background-color: white; padding: 5px; border-radius: 4px;">
            <img src="{url_leyenda_anomalia}" 
                 alt="Leyenda TVDI Anomalía"
                 style="max-width: 100%; 
                        height: auto;
                        border-radius: 3px;
                        display: block;">
        </div>
    </div>

    <div id="btnLeyendaAnomalia" style="position: fixed;
            bottom: 85px; left: 10px;
            background-color: #FF9800;
            color: white;
            padding: 6px 10px;
            border-radius: 5px;
            z-index: 9996;
            cursor: pointer;
            font-family: Arial, sans-serif;
            font-size: 10px;
            display: none;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            align-items: center;
            gap: 5px;
            border: 1px solid #F57C00;"
            onclick="mostrarLeyendaTvdi('anomalia')"
            title="Mostrar leyenda TVDI Anomalía"
            onmouseover="this.style.backgroundColor='#F57C00'; this.style.transform='translateY(-1px)';"
            onmouseout="this.style.backgroundColor='#FF9800'; this.style.transform='translateY(0)';">
        <span style="font-size: 12px;">🟡</span>
        <span style="color: white;">Leyenda</span>
    </div>
    '''
    
    # LEYENDA IMERG
    leyenda_imerg_html = f'''
    <div id="leyendaImerg" style="position: fixed;
            bottom: 120px; left: 10px;
            background-color: white;
            padding: 8px;
            border-radius: 6px;
            border: 2px solid #1E88E5;
            z-index: 9996;
            width: 160px;
            display: none;
            box-shadow: 0 4px 15px rgba(0,0,0,0.25);">
    
        <div style="display: flex; justify-content: space-between; 
                    align-items: center; margin-bottom: 8px; padding-bottom: 6px;
                    border-bottom: 1px solid #e0e0e0;">
            <div style="font-size: 11px; font-weight: bold; color: #1E88E5;">
                🌧️ Precipitación IMERG
            </div>
            <button onclick="ocultarLeyendaImerg()"
                    style="background: none; border: none; color: #666;
                           font-size: 16px; cursor: pointer; padding: 0;
                           line-height: 1; width: 20px; height: 20px;
                           display: flex; align-items: center; justify-content: center;
                           border-radius: 2px;"
                    title="Cerrar leyenda">
                ×
            </button>
        </div>
    
        <div style="text-align: center; background-color: white; padding: 5px; border-radius: 4px;">
            <img src="{url_leyenda_imerg}" 
                 alt="Leyenda Precipitación IMERG"
                 style="max-width: 70%; 
                        height: auto;
                        border-radius: 3px;
                        display: block;">
        </div>
    </div>
    
    <div id="btnLeyendaImerg" style="position: fixed;
            bottom: 85px; left: 10px;
            background-color: #1E88E5;
            color: white;
            padding: 6px 10px;
            border-radius: 5px;
            z-index: 9996;
            cursor: pointer;
            font-family: Arial, sans-serif;
            font-size: 10px;
            display: none;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            align-items: center;
            gap: 5px;
            border: 1px solid #0D47A1;"
            onclick="mostrarLeyendaImerg()"
            title="Mostrar leyenda Precipitación IMERG"
            onmouseover="this.style.backgroundColor='#0D47A1'; this.style.transform='translateY(-1px)';"
            onmouseout="this.style.backgroundColor='#1E88E5'; this.style.transform='translateY(0)';">
        <span style="font-size: 12px;">🌧️</span>
        <span style="color: white;">Leyenda</span>
    </div>
    '''
    
    # LEYENDA HUMEDAD SUELO
    leyenda_humedad_html = '''
    <div id="leyendaHumedad" style="position: fixed;
            bottom: 120px; left: 10px;
            background-color: white;
            padding: 10px 12px;
            border-radius: 6px;
            border: 2px solid #795548;
            z-index: 9996;
            font-family: Arial, sans-serif;
            font-size: 11px;
            width: 140px;
            display: none;
            box-shadow: 0 4px 15px rgba(0,0,0,0.25);">
    
        <div style="font-weight: bold; color: #795548;
                    margin-bottom: 8px; border-bottom: 2px solid #795548;
                    padding-bottom: 6px; font-size: 10px;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span>💧</span>
                    <span>Humedad Suelo (%)</span>
                </div>
                <button onclick="ocultarLeyendaHumedad()"
                        style="background: none; border: none; color: #795548;
                               font-size: 16px; cursor: pointer; padding: 0;
                               line-height: 1;">×</button>
            </div>
        </div>
    
        <div style="margin-bottom: 10px;">
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div style="width: 16px; height: 16px; background-color: #FF0000;
                            margin-right: 8px; border: 1px solid #CC0000; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 9px;">0%</span>
                    <span style="font-size: 9px;">2%</span>
                </div>
            </div>
    
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div style="width: 16px; height: 16px; background-color: #FF6600;
                            margin-right: 8px; border: 1px solid #CC5500; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 9px;">2%</span>
                    <span style="font-size: 9px;">5%</span>
                </div>
            </div>
    
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div style="width: 16px; height: 16px; background-color: #FFCC00;
                            margin-right: 8px; border: 1px solid #CCA300; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 9px;">5%</span>
                    <span style="font-size: 9px;">10%</span>
                </div>
            </div>
    
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div style="width: 16px; height: 16px; background-color: #00FF00;
                            margin-right: 8px; border: 1px solid #00CC00; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 9px;">10%</span>
                    <span style="font-size: 9px;">20%</span>
                </div>
            </div>
    
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div style="width: 16px; height: 16px; background-color: #00FFFF;
                            margin-right: 8px; border: 1px solid #00CCCC; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 9px;">20%</span>
                    <span style="font-size: 9px;">30%</span>
                </div>
            </div>
    
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div style="width: 16px; height: 16px; background-color: #0066FF;
                            margin-right: 8px; border: 1px solid #0055CC; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 9px;">30%</span>
                    <span style="font-size: 9px;">45%</span>
                </div>
            </div>
    
            <div style="display: flex; align-items: center;">
                <div style="width: 16px; height: 16px; background-color: #0000FF;
                            margin-right: 8px; border: 1px solid #0000CC; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 9px; font-weight: bold;">> 45%</span>
                    <span style="font-size: 9px;"></span>
                </div>
            </div>
        </div>
    </div>
    
    <div id="btnLeyendaHumedad" style="position: fixed;
            bottom: 85px; left: 10px;
            background-color: #795548;
            color: white;
            padding: 6px 10px;
            border-radius: 5px;
            z-index: 9996;
            cursor: pointer;
            font-family: Arial, sans-serif;
            font-size: 10px;
            display: none;
            box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            align-items: center;
            gap: 5px;
            border: 1px solid #5D4037;"
            onclick="mostrarLeyendaHumedad()"
            title="Mostrar leyenda Humedad de Suelo"
            onmouseover="this.style.backgroundColor='#5D4037'; this.style.transform='translateY(-1px)';"
            onmouseout="this.style.backgroundColor='#795548'; this.style.transform='translateY(0)';">
        <span style="font-size: 12px;">💧</span>
        <span style="color: white;">Leyenda</span>
    </div>
    '''
    
    # LEYENDA SINIESTROS (solo si hay siniestros)
    if campos['causa_stro'] and gdf[campos['causa_stro']].notna().any():
        leyenda_siniestros_boton = '''
        <div id="btnLeyendaSiniestros" style="position: fixed;
                bottom: 85px; left: 10px;
                background-color: #F44336;
                color: white;
                padding: 6px 10px;
                border-radius: 5px;
                z-index: 9996;
                cursor: pointer;
                font-family: Arial, sans-serif;
                font-size: 10px;
                display: none;
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
                align-items: center;
                gap: 5px;
                border: 1px solid #D32F2F;"
                onclick="mostrarLeyendaSiniestros()"
                title="Mostrar leyenda de Siniestros"
                onmouseover="this.style.backgroundColor='#D32F2F'; this.style.transform='translateY(-1px)';"
                onmouseout="this.style.backgroundColor='#F44336'; this.style.transform='translateY(0)';">
            <span style="font-size: 12px;">⚠️</span>
            <span style="color: white;">Leyenda</span>
        </div>
        
        <div id="leyendaSiniestros" style="position: fixed;
                bottom: 120px; left: 180px;
                background-color: white;
                padding: 10px 12px;
                border-radius: 8px;
                border: 2px solid #F44336;
                z-index: 9996;
                font-family: Arial, sans-serif;
                font-size: 11px;
                width: 140px;
                display: none;
                box-shadow: 0 4px 15px rgba(0,0,0,0.25);">
    
            <div style="display: flex; justify-content: space-between; 
                        align-items: center; margin-bottom: 8px; padding-bottom: 6px;
                        border-bottom: 1px solid #e0e0e0;">
                <div style="font-size: 11px; font-weight: bold; color: #F44336;">
                    ⚠️ Siniestros
                </div>
                <button onclick="ocultarLeyendaSiniestros()"
                        style="background: none; border: none; color: #666;
                               font-size: 16px; cursor: pointer; padding: 0;
                               line-height: 1; width: 20px; height: 20px;
                               display: flex; align-items: center; justify-content: center;
                               border-radius: 2px;"
                        title="Cerrar leyenda">
                    ×
                </button>
            </div>
    
            <div style="margin-bottom: 8px;">
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <div style="width: 14px; height: 14px; background-color: #00BCD4;
                                margin-right: 8px; border: 1px solid #0097A7; border-radius: 3px;"></div>
                    <div style="flex: 1; font-size: 10px;">Granizo</div>
                </div>
    
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <div style="width: 14px; height: 14px; background-color: #FF5252;
                                margin-right: 8px; border: 1px solid #D50000; border-radius: 3px;"></div>
                    <div style="flex: 1; font-size: 10px;">Sequía</div>
                </div>
    
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <div style="width: 14px; height: 14px; background-color: #448AFF;
                                margin-right: 8px; border: 1px solid #2979FF; border-radius: 3px;"></div>
                    <div style="flex: 1; font-size: 10px;">Inundación</div>
                </div>
    
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <div style="width: 14px; height: 14px; background-color: #7C4DFF;
                                margin-right: 8px; border: 1px solid #651FFF; border-radius: 3px;"></div>
                    <div style="flex: 1; font-size: 10px;">Viento</div>
                </div>
    
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <div style="width: 14px; height: 14px; background-color: #795548;
                                margin-right: 8px; border: 1px solid #5D4037; border-radius: 3px;"></div>
                    <div style="flex: 1; font-size: 10px;">Incendio</div>
                </div>
    
                <div style="display: flex; align-items: center;">
                    <div style="width: 14px; height: 14px; background-color: #FFFFFF;
                                margin-right: 8px; border: 1px solid #E0E0E0; border-radius: 3px;"></div>
                    <div style="flex: 1; font-size: 10px;">Helada</div>
                </div>
            </div>
        </div>
        
        <script>
        function mostrarLeyendaSiniestros() {
            document.getElementById("leyendaSiniestros").style.display = "block";
            document.getElementById("btnLeyendaSiniestros").style.display = "none";
        }
        
        function ocultarLeyendaSiniestros() {
            document.getElementById("leyendaSiniestros").style.display = "none";
            document.getElementById("btnLeyendaSiniestros").style.display = "flex";
        }
        
        function detectarSiniestros() {
            var checkboxes = document.querySelectorAll("input[type='checkbox']");
            var siniestrosActivo = false;
            
            checkboxes.forEach(function(checkbox) {
                var label = checkbox.parentElement;
                if (label && label.textContent) {
                    if (label.textContent.includes("⚠️ Siniestros")) {
                        if (checkbox.checked) {
                            siniestrosActivo = true;
                        }
                    }
                }
            });
            
            if (siniestrosActivo) {
                document.getElementById("btnLeyendaSiniestros").style.display = "flex";
            } else {
                document.getElementById("btnLeyendaSiniestros").style.display = "none";
                document.getElementById("leyendaSiniestros").style.display = "none";
            }
        }
        
        document.addEventListener("DOMContentLoaded", function() {
            setTimeout(function() {
                var checkboxes = document.querySelectorAll("input[type='checkbox']");
                checkboxes.forEach(function(checkbox) {
                    checkbox.addEventListener("change", detectarSiniestros);
                });
                
                if (typeof map !== "undefined") {
                    map.on("overlayadd overlayremove", function(e) {
                        if (e.name && e.name.includes("⚠️ Siniestros")) {
                            setTimeout(detectarSiniestros, 100);
                        }
                    });
                }
                
                detectarSiniestros();
            }, 1500);
        });
        </script>
        '''
        
        agregar_elemento_html_seguro(m, leyenda_siniestros_boton)

    # Agregar todas las leyendas
    agregar_elemento_html_seguro(m, leyenda_normal_html)
    agregar_elemento_html_seguro(m, leyenda_anomalia_html)
    agregar_elemento_html_seguro(m, leyenda_imerg_html)
    agregar_elemento_html_seguro(m, leyenda_humedad_html)

    # ========== JAVASCRIPT PARA LEYENDAS (100% IDÉNTICO) ==========
    js_leyendas_completo = '''
    <script>
    // FUNCIONES TVDI
    function mostrarLeyendaTvdi(tipo) {
        console.log("Mostrando leyenda TVDI:", tipo);
        ocultarTodasLeyendas();
        
        if (tipo === 'normal') {
            document.getElementById("leyendaNormal").style.display = "block";
            document.getElementById("btnLeyendaNormal").style.display = "none";
        } else if (tipo === 'anomalia') {
            document.getElementById("leyendaAnomalia").style.display = "block";
            document.getElementById("btnLeyendaAnomalia").style.display = "none";
        }
    }
    
    function ocultarLeyendaTvdi(tipo) {
        console.log("Ocultando leyenda TVDI:", tipo);
        if (tipo === 'normal') {
            document.getElementById("leyendaNormal").style.display = "none";
            document.getElementById("btnLeyendaNormal").style.display = "flex";
        } else if (tipo === 'anomalia') {
            document.getElementById("leyendaAnomalia").style.display = "none";
            document.getElementById("btnLeyendaAnomalia").style.display = "flex";
        }
    }
    
    // FUNCIONES IMERG
    function mostrarLeyendaImerg() {
        console.log("Mostrando leyenda IMERG");
        ocultarTodasLeyendas();
        document.getElementById("leyendaImerg").style.display = "block";
        document.getElementById("btnLeyendaImerg").style.display = "none";
    }
    
    function ocultarLeyendaImerg() {
        console.log("Ocultando leyenda IMERG");
        document.getElementById("leyendaImerg").style.display = "none";
        document.getElementById("btnLeyendaImerg").style.display = "flex";
    }
    
    // FUNCIONES HUMEDAD
    function mostrarLeyendaHumedad() {
        console.log("Mostrando leyenda Humedad");
        ocultarTodasLeyendas();
        document.getElementById("leyendaHumedad").style.display = "block";
        document.getElementById("btnLeyendaHumedad").style.display = "none";
    }
    
    function ocultarLeyendaHumedad() {
        console.log("Ocultando leyenda Humedad");
        document.getElementById("leyendaHumedad").style.display = "none";
        document.getElementById("btnLeyendaHumedad").style.display = "flex";
    }
    
    // FUNCIÓN PARA OCULTAR TODAS
    function ocultarTodasLeyendas() {
        document.getElementById("leyendaNormal").style.display = "none";
        document.getElementById("leyendaAnomalia").style.display = "none";
        document.getElementById("leyendaImerg").style.display = "none";
        document.getElementById("leyendaHumedad").style.display = "none";
        document.getElementById("leyendaSiniestros").style.display = "none";
        
        document.getElementById("btnLeyendaNormal").style.display = "none";
        document.getElementById("btnLeyendaAnomalia").style.display = "none";
        document.getElementById("btnLeyendaImerg").style.display = "none";
        document.getElementById("btnLeyendaHumedad").style.display = "none";
        document.getElementById("btnLeyendaSiniestros").style.display = "none";
    }
    
    // SISTEMA INTELIGENTE PARA DETECTAR CAPAS WMS
    function detectarCapasWMS() {
        console.log("=== DETECTANDO CAPAS WMS ===");
        
        var checkboxes = document.querySelectorAll('input[type="checkbox"]');
        var imergActiva = false;
        var humedadActiva = false;
        var tvdiNormalActiva = false;
        var tvdiAnomaliaActiva = false;
        var siniestrosActiva = false;
        
        checkboxes.forEach(function(checkbox) {
            var label = checkbox.parentElement;
            if (label && label.textContent) {
                var texto = label.textContent.trim();
                
                if ((texto.includes("🌧️ PP") || texto.includes("IMERG")) && 
                    !texto.includes("CHIRPS")) {
                    if (checkbox.checked) imergActiva = true;
                }
                
                if (texto.includes("💧 Humedad") || texto.includes("Humedad")) {
                    if (checkbox.checked) humedadActiva = true;
                }
                
                if ((texto.includes("TVDI") || texto.includes("📊")) && 
                    !texto.includes("Anomalía") && 
                    !texto.includes("🟡") &&
                    !texto.includes("anom")) {
                    if (checkbox.checked) tvdiNormalActiva = true;
                }
                
                if (texto.includes("Anomalía") || 
                    texto.includes("🟡") || 
                    texto.includes("anom") ||
                    texto.toLowerCase().includes("anomalia")) {
                    if (checkbox.checked) tvdiAnomaliaActiva = true;
                }
                
                if (texto.includes("⚠️ Siniestros")) {
                    if (checkbox.checked) siniestrosActiva = true;
                }
            }
        });
        
        console.log("Resultado: IMERG=" + imergActiva + ", Humedad=" + humedadActiva + 
                   ", TVDI_Normal=" + tvdiNormalActiva + ", TVDI_Anomalia=" + tvdiAnomaliaActiva +
                   ", Siniestros=" + siniestrosActiva);
        
        // Mostrar botones según prioridad
        ocultarTodasLeyendas();
        
        if (imergActiva) {
            document.getElementById("btnLeyendaImerg").style.display = "flex";
        }
        else if (humedadActiva) {
            document.getElementById("btnLeyendaHumedad").style.display = "flex";
        }
        else if (tvdiNormalActiva) {
            document.getElementById("btnLeyendaNormal").style.display = "flex";
        }
        else if (tvdiAnomaliaActiva) {
            document.getElementById("btnLeyendaAnomalia").style.display = "flex";
        }
        else if (siniestrosActiva) {
            document.getElementById("btnLeyendaSiniestros").style.display = "flex";
        }
    }
    
    function inicializarSistemaLeyendasWMS() {
        console.log("🚀 Inicializando sistema de leyendas...");
        
        var checkboxes = document.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(function(checkbox) {
            checkbox.addEventListener("change", function() {
                setTimeout(detectarCapasWMS, 100);
            });
        });
        
        if (typeof map !== "undefined") {
            map.on("overlayadd overlayremove", function(e) {
                console.log("🗺️ Evento mapa:", e.name);
                setTimeout(detectarCapasWMS, 100);
            });
        }
        
        setTimeout(function() {
            console.log("🔍 Estado inicial de capas WMS...");
            detectarCapasWMS();
        }, 2000);
        
        console.log("✅ Sistema de leyendas inicializado");
    }
    
    document.addEventListener("DOMContentLoaded", inicializarSistemaLeyendasWMS);
    
    if (typeof map !== "undefined") {
        map.whenReady(inicializarSistemaLeyendasWMS);
    }
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            ocultarTodasLeyendas();
            setTimeout(detectarCapasWMS, 100);
        }
    });
    </script>
    '''
    
    agregar_elemento_html_seguro(m, js_leyendas_completo)

    # ========== CONTROLES (100% IDÉNTICOS) ==========
    folium.LayerControl(position='topright', collapsed=True).add_to(m)
    Fullscreen(
        position='topright',
        title='Pantalla completa',
        title_cancel='Salir pantalla completa'
    ).add_to(m)
    MeasureControl(position='topright').add_to(m)

    # ========== BOTÓN PARA SUBIR FOTOS ==========
    boton_fotos_html = '''
    <!-- BOTÓN EN EL PANEL DE CONTROLES -->
    <div id="controlSubirFotos" style="
        position: absolute;
        top: 230px;  /* Debajo del botón de Medir */
        right: 10px;
        z-index: 1000;
    ">
        <a class="leaflet-bar-part leaflet-bar-part-single" 
           href="#" 
           title="📸 Subir foto desde campo"
           style="
                display: block;
                width: 30px;
                height: 30px;
                background: linear-gradient(135deg, #4CAF50, #2E7D32);
                border-radius: 4px;
                border: 2px solid rgba(255, 255, 255, 0.8);
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                text-align: center;
                line-height: 30px;
                font-size: 18px;
                color: white;
                text-decoration: none;
                cursor: pointer;
                margin-bottom: 5px;
           ">
            📸
        </a>
    </div>

    <!-- PANEL FLOTANTE PARA SUBIR FOTOS -->
    <div id="panelSubirFoto" style="
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 20px;
        border-radius: 15px;
        border: 3px solid #4CAF50;
        z-index: 10002;
        display: none;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        width: 90%;
        max-width: 400px;
        font-family: Arial, sans-serif;
    ">

        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <div style="font-size: 18px; font-weight: bold; color: #2E7D32;">
                📸 Subir foto desde campo
            </div>
            <button onclick="cerrarPanelFoto()" style="background: none; border: none; font-size: 24px; cursor: pointer; color: #666;">×</button>
        </div>

        <div id="contenidoSubir">
            <div id="paso1" style="text-align: center;">
                <button onclick="tomarFotoConCamara()" style="
                    width: 100%; 
                    padding: 15px; 
                    margin-bottom: 10px;
                    background: #4CAF50; 
                    color: white; 
                    border: none;
                    border-radius: 10px; 
                    font-size: 16px; 
                    cursor: pointer;
                ">
                    📷 Tomar foto con cámara
                </button>
                
                <div style="margin: 15px 0; color: #666; font-size: 14px;">
                    ─── o ───
                </div>
                
                <button onclick="seleccionarFotoArchivo()" style="
                    width: 100%; 
                    padding: 15px;
                    background: #2196F3; 
                    color: white; 
                    border: none;
                    border-radius: 10px; 
                    font-size: 16px; 
                    cursor: pointer;
                ">
                    📁 Seleccionar foto existente
                </button>
                
                <input type="file" id="inputFotoArchivo" accept="image/*" style="display: none;" capture="environment">
            </div>

            <div id="paso2" style="display: none;">
                <div style="text-align: center; margin-bottom: 15px;">
                    <img id="previewFoto" src="" style="
                        max-width: 100%; 
                        max-height: 300px; 
                        border-radius: 10px; 
                        border: 2px solid #ddd;
                    ">
                </div>
                
                <div style="margin-bottom: 15px;">
                    <div style="font-weight: bold; margin-bottom: 5px; color: #666;">
                        📍 Ubicación GPS:
                    </div>
                    <div id="infoGPS" style="font-size: 12px; color: #4CAF50;">
                        Obteniendo ubicación...
                    </div>
                </div>
                
                <button onclick="subirFoto()" id="btnSubirFoto" style="
                    width: 100%; 
                    padding: 15px;
                    background: linear-gradient(135deg, #4CAF50, #2E7D32);
                    color: white; 
                    border: none;
                    border-radius: 10px; 
                    font-size: 16px; 
                    cursor: pointer; 
                    font-weight: bold;
                ">
                    ⬆️ Subir foto al mapa
                </button>
            </div>

            <div id="paso3" style="display: none; text-align: center;">
                <div style="margin-bottom: 20px;">
                    <div style="
                        width: 50px; 
                        height: 50px; 
                        margin: 0 auto 15px;
                        border: 3px solid #f3f3f3; 
                        border-top: 3px solid #4CAF50;
                        border-radius: 50%; 
                        animation: spin 1s linear infinite;
                    "></div>
                    <div id="mensajeProgreso" style="font-weight: bold; color: #2E7D32;">
                        Subiendo foto...
                    </div>
                </div>
                
                <div id="infoSubida" style="font-size: 12px; color: #666;">
                    Esto puede tomar unos segundos
                </div>
            </div>
        </div>

        <div style="
            margin-top: 20px; 
            padding-top: 15px; 
            border-top: 1px solid #eee;
            font-size: 11px; 
            color: #888; 
            text-align: center;
        ">
            <div>📍 La foto aparecerá en el mapa en 2 minutos</div>
            <div>📱 Funciona con o sin internet</div>
        </div>
    </div>

    <!-- OVERLAY OSCURO -->
    <div id="overlayFoto" style="
        position: fixed; 
        top: 0; 
        left: 0; 
        width: 100%; 
        height: 100%; 
        background: rgba(0,0,0,0.7);
        z-index: 10001; 
        display: none;
    "></div>

    <style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .leaflet-top .leaflet-control {
        margin-top: 10px;
    }
    
    #controlSubirFotos a:hover {
        background: linear-gradient(135deg, #45a049, #1b5e20);
        transform: scale(1.05);
        transition: all 0.2s;
    }
    </style>

    <script>
    // Variables globales
    let fotoActual = null;
    let gpsActual = null;
    let estaEnLinea = navigator.onLine;

    // ========== FUNCIONES DEL PANEL ==========
    function abrirPanelSubirFoto() {
        document.getElementById('panelSubirFoto').style.display = 'block';
        document.getElementById('overlayFoto').style.display = 'block';
        document.getElementById('paso1').style.display = 'block';
        document.getElementById('paso2').style.display = 'none';
        document.getElementById('paso3').style.display = 'none';
        
        obtenerUbicacionGPS();
    }

    function cerrarPanelFoto() {
        document.getElementById('panelSubirFoto').style.display = 'none';
        document.getElementById('overlayFoto').style.display = 'none';
        fotoActual = null;
    }

    // ========== OBTENER GPS ==========
    function obtenerUbicacionGPS() {
        const infoGPS = document.getElementById('infoGPS');
        
        if (!navigator.geolocation) {
            infoGPS.innerHTML = '❌ GPS no disponible en este dispositivo';
            gpsActual = null;
            return;
        }
        
        infoGPS.innerHTML = '📍 Obteniendo ubicación...';
        
        navigator.geolocation.getCurrentPosition(
            function(posicion) {
                const lat = posicion.coords.latitude.toFixed(6);
                const lon = posicion.coords.longitude.toFixed(6);
                const precision = posicion.coords.accuracy.toFixed(0);
                
                gpsActual = {
                    lat: parseFloat(lat),
                    lon: parseFloat(lon),
                    precision: precision
                };
                
                infoGPS.innerHTML = `📍 ${lat}, ${lon} (precisión: ${precision}m)`;
                infoGPS.style.color = '#4CAF50';
            },
            function(error) {
                console.error('Error GPS:', error);
                gpsActual = null;
                infoGPS.innerHTML = '⚠️ No se pudo obtener ubicación. Se usará ubicación aproximada.';
                infoGPS.style.color = '#FF9800';
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    }

    // ========== TOMAR FOTO ==========
    function tomarFotoConCamara() {
        const input = document.getElementById('inputFotoArchivo');
        input.setAttribute('capture', 'environment');
        input.click();
    }

    function seleccionarFotoArchivo() {
        const input = document.getElementById('inputFotoArchivo');
        input.removeAttribute('capture');
        input.click();
    }

    // Configurar el input de archivo
    document.getElementById('inputFotoArchivo').addEventListener('change', function(e) {
        const archivo = e.target.files[0];
        if (!archivo) return;
        
        const reader = new FileReader();
        reader.onload = function(event) {
            fotoActual = event.target.result;
            
            document.getElementById('previewFoto').src = fotoActual;
            document.getElementById('paso1').style.display = 'none';
            document.getElementById('paso2').style.display = 'block';
            
            if (!gpsActual) {
                obtenerUbicacionGPS();
            }
        };
        reader.readAsDataURL(archivo);
    });

    // ========== SUBIR FOTO ==========
    async function subirFoto() {
        if (!fotoActual) {
            alert('Por favor, selecciona una foto primero');
            return;
        }
        
        document.getElementById('paso2').style.display = 'none';
        document.getElementById('paso3').style.display = 'block';
        
        const btnSubir = document.getElementById('btnSubirFoto');
        const mensajeProgreso = document.getElementById('mensajeProgreso');
        const infoSubida = document.getElementById('infoSubida');
        
        btnSubir.disabled = true;
        
        const timestamp = Date.now();
        const nombreArchivo = `foto_${gpsActual ? gpsActual.lat + '_' + gpsActual.lon + '_' : ''}${timestamp}.jpg`;
        
        const base64Data = fotoActual.split(',')[1];
        
        // Verificar conexión
        estaEnLinea = navigator.onLine;
        
        if (!estaEnLinea) {
            guardarFotoOffline(base64Data, nombreArchivo);
            mensajeProgreso.innerHTML = '✅ Guardada localmente (offline)';
            infoSubida.innerHTML = 'Se subirá automáticamente cuando haya conexión';
            
            setTimeout(() => {
                cerrarPanelFoto();
                mostrarNotificacion('📸 Foto guardada (modo offline)', 'success');
            }, 2000);
            return;
        }
        
        // MODO ONLINE: Subir a GitHub usando el workflow
        mensajeProgreso.innerHTML = '🌐 Subiendo a GitHub...';
        
        try {
            // Formatear datos para enviar
            const fotoData = {
                nombre: nombreArchivo,
                datos: base64Data,
                lat: gpsActual ? gpsActual.lat : -31.4201,
                lon: gpsActual ? gpsActual.lon : -64.1888,
                timestamp: new Date().toISOString()
            };
            
            // ========== NUEVA FUNCIÓN PARA USAR EL WORKFLOW ==========
            async function subirFotoConWorkflow(fotoData) {
                console.log('🔄 Enviando foto a GitHub Actions...');
                
                const nombreArchivo = `foto_${Math.abs(fotoData.lat).toFixed(6)}_${Math.abs(fotoData.lon).toFixed(6)}_${Date.now()}.jpg`;
                
                try {
                    // Usar GitHub API para trigger workflow
                    const response = await fetch(
                        'https://api.github.com/repos/franciscotomatis/APP-C-rdoba/actions/workflows/recibir-foto.yml/dispatches',
                        {
                            method: 'POST',
                            headers: {
                                'Accept': 'application/vnd.github.v3+json',
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                ref: 'main',
                                inputs: {
                                    foto_base64: fotoData.datos,
                                    nombre_archivo: nombreArchivo,
                                    latitud: fotoData.lat.toString(),
                                    longitud: fotoData.lon.toString()
                                }
                            })
                        }
                    );
                    
                    if (response.ok) {
                        console.log('✅ Workflow ejecutado correctamente');
                        return { success: true };
                    } else {
                        console.error('❌ Error ejecutando workflow');
                        return { success: false };
                    }
                    
                } catch (error) {
                    console.error('❌ Error de red:', error);
                    return { success: false };
                }
            }
            
            // Usar la nueva función
            const resultado = await subirFotoConWorkflow(fotoData);
            
            if (resultado.success) {  // ✅ Esto está bien
                mensajeProgreso.innerHTML = '✅ Foto subida exitosamente';
                infoSubida.innerHTML = 'Aparecerá en el mapa en 2 minutos';
                
                setTimeout(() => {
                    cerrarPanelFoto();
                    mostrarNotificacion('✅ Foto subida al mapa', 'success');
                    
                    // Recargar capa de fotos
                    if (window.capaFotosGithub) {
                        window.capaFotosGithub.clearLayers();
                        if (typeof cargarFotosDesdeGithub === 'function') {
                            cargarFotosDesdeGithub();
                        }
                    }
                }, 2000);
            } else {
                throw new Error('Error en subida');
            }
            
        } catch (error) {
            console.error('Error subiendo foto:', error);
            
            // Fallback: guardar offline
            guardarFotoOffline(base64Data, nombreArchivo);
            
            mensajeProgreso.innerHTML = '⚠️ Guardada localmente';
            infoSubida.innerHTML = 'Error de conexión. Se intentará más tarde.';
            
            setTimeout(() => {
                cerrarPanelFoto();
                mostrarNotificacion('📸 Foto guardada (se subirá luego)', 'warning');
            }, 2000);
        }
    }
   
    function guardarParaSubidaManual(fotoData, nombreArchivo) {
        // Usar MISMA lista que offline para simplificar
        const fotosOffline = JSON.parse(localStorage.getItem('fotosOffline') || '[]');
        
        fotosOffline.push({
            id: Date.now(),
            nombre: nombreArchivo,
            datos: fotoData.datos,
            gps: { lat: fotoData.lat, lon: fotoData.lon },
            timestamp: new Date().toISOString(),
            estado: 'pendiente',
            intentos: 0
        });
        
        localStorage.setItem('fotosOffline', JSON.stringify(fotosOffline));
        
        // Mostrar botón de pendientes
        actualizarBotonPendientes(fotosOffline.length);
        
        console.log('📸 Foto guardada para subida manual');
        
        return {
            success: false,
            mensaje: 'Guardada para subida manual',
            cantidad: fotosOffline.length
        };
    }
    
    function actualizarBotonPendientes(cantidad) {
        // Buscar o crear botón
        let boton = document.getElementById('btnFotosPendientes');
        
        if (!boton && cantidad > 0) {
            boton = document.createElement('div');
            boton.id = 'btnFotosPendientes';
            boton.style.position = 'fixed';
            boton.style.bottom = '80px';
            boton.style.right = '20px';
            boton.style.zIndex = '9998';
            document.body.appendChild(boton);
        }
        
        if (cantidad > 0 && boton) {
            boton.innerHTML = `
                <button onclick="mostrarFotosPendientes()" style="
                    background: #FF9800;
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 8px;
                    font-family: Arial, sans-serif;
                    font-size: 12px;
                    cursor: pointer;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.2);
                ">
                    📋 ${cantidad} foto(s) pendientes
                </button>
            `;
        } else if (boton && cantidad === 0) {
            boton.remove();
        }
    }

    // ========== MODO OFFLINE ==========
    function guardarFotoOffline(base64Data, nombreArchivo) {
        const fotosOffline = JSON.parse(localStorage.getItem('fotosOffline') || '[]');
        
        const fotoOffline = {
            id: Date.now(),
            nombre: nombreArchivo,
            datos: base64Data,
            gps: gpsActual,
            timestamp: new Date().toISOString(),
            estado: 'pendiente'
        };
        
        fotosOffline.push(fotoOffline);
        localStorage.setItem('fotosOffline', JSON.stringify(fotosOffline));
        
        console.log('📸 Foto guardada offline');
        
        programarSincronizacion();
    }

    function programarSincronizacion() {
        window.addEventListener('online', function sincronizarAlConectar() {
            console.log('📶 Conexión recuperada, sincronizando fotos...');
            sincronizarFotosOffline();
            window.removeEventListener('online', sincronizarAlConectar);
        });
    }

    async function sincronizarFotosOffline() {
        const fotosOffline = JSON.parse(localStorage.getItem('fotosOffline') || '[]');
        if (fotosOffline.length === 0) return;
        
        console.log(`🔄 Intentando subir ${fotosOffline.length} fotos offline...`);
        
        // Intentar subir cada foto
        const fotosExitosas = [];
        const fotosFallidas = [];
        
        for (const foto of fotosOffline) {
            try {
                // Intentar subir usando la misma función
                const resultado = await subirAGitHubAPI({
                    datos: foto.datos,
                    lat: foto.gps.lat,
                    lon: foto.gps.lon,
                    nombre: foto.nombre
                });
                
                if (resultado.success) {
                    fotosExitosas.push(foto);
                } else {
                    foto.intentos = (foto.intentos || 0) + 1;
                    fotosFallidas.push(foto);
                }
                
                // Esperar 1 segundo entre subidas
                await new Promise(resolve => setTimeout(resolve, 1000));
                
            } catch (error) {
                console.error('Error subiendo foto offline:', error);
                foto.intentos = (foto.intentos || 0) + 1;
                fotosFallidas.push(foto);
            }
        }
        
        // Actualizar localStorage
        if (fotosExitosas.length > 0) {
            // Eliminar solo las exitosas
            const nuevasFotos = fotosOffline.filter(f => 
                !fotosExitosas.some(exitosa => exitosa.id === f.id)
            );
            localStorage.setItem('fotosOffline', JSON.stringify(nuevasFotos));
            
            mostrarNotificacion(`✅ ${fotosExitosas.length} fotos subidas`, 'success');
        }
        
        // Actualizar botón
        actualizarBotonPendientes(fotosFallidas.length);
        
        console.log(`Resultado: ${fotosExitosas.length} exitosas, ${fotosFallidas.length} fallidas`);
    }

    // ========== NOTIFICACIONES ==========
    function mostrarNotificacion(mensaje, tipo = 'info') {
        const notificacion = document.createElement('div');
        notificacion.style.position = 'fixed';
        notificacion.style.bottom = '20px';
        notificacion.style.right = '20px';
        notificacion.style.padding = '12px 20px';
        notificacion.style.borderRadius = '8px';
        notificacion.style.fontFamily = 'Arial, sans-serif';
        notificacion.style.fontSize = '14px';
        notificacion.style.zIndex = '10003';
        notificacion.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        
        const colores = {
            success: { bg: '#4CAF50', color: 'white' },
            warning: { bg: '#FF9800', color: 'white' },
            info: { bg: '#2196F3', color: 'white' }
        };
        
        notificacion.style.background = colores[tipo]?.bg || '#2196F3';
        notificacion.style.color = colores[tipo]?.color || 'white';
        notificacion.textContent = mensaje;
        
        document.body.appendChild(notificacion);
        
        setTimeout(() => {
            notificacion.style.opacity = '0';
            notificacion.style.transition = 'opacity 0.5s';
            setTimeout(() => {
                if (notificacion.parentNode) {
                    notificacion.parentNode.removeChild(notificacion);
                }
            }, 500);
        }, 3000);
    }

    // ========== CONFIGURACIÓN INICIAL ==========
    document.addEventListener('DOMContentLoaded', function() {
        // Configurar el botón del panel
        const botonSubir = document.querySelector('#controlSubirFotos a');
        if (botonSubir) {
            botonSubir.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                abrirPanelSubirFoto();
            });
        }
        
        // Verificar fotos pendientes al cargar
        setTimeout(() => {
            const fotosPendientes = JSON.parse(localStorage.getItem('fotosOffline') || '[]');
            if (fotosPendientes.length > 0 && navigator.onLine) {
                sincronizarFotosOffline();
            }
        }, 5000);
    });

    // Detectar cambios de conexión
    window.addEventListener('online', function() {
        estaEnLinea = true;
        mostrarNotificacion('📶 Conectado a internet', 'success');
    });

    window.addEventListener('offline', function() {
        estaEnLinea = false;
        mostrarNotificacion('⚠️ Sin conexión - Modo offline', 'warning');
    });
    </script>
    '''

    # Agregar el HTML al mapa
    agregar_elemento_html_seguro(m, boton_fotos_html)

    # ========== GPS AUTO-ACTIVADO (100% IDÉNTICO) ==========
    try:
        locate = LocateControl(
            position='topright',
            drawCircle=True,
            follow=True,
            showPopup=True,
            keepCurrentZoomLevel=False,
            initialZoom=15,
            strings={
                'title': 'Mi ubicación actual',
                'popup': 'Tu ubicación: {distance} {unit} desde aquí',
                'metersUnit': 'metros',
                'feetUnit': 'pies'
            },
            locateOptions={
                'enableHighAccuracy': True,
                'maximumAge': 30000,
                'timeout': 27000,
                'watch': True
            }
        ).add_to(m)
        
        print("✅ 📍 Geolocalización configurada")
        
        gps_auto_html = '''
        <script>
        setTimeout(function() {
            var gpsButtons = document.querySelectorAll('.leaflet-control-locate a');
            if (gpsButtons.length > 0) {
                console.log("📍 Activando GPS automáticamente...");
                gpsButtons[0].click();
                
                var gpsControl = document.querySelector('.leaflet-control-locate');
                if (gpsControl) {
                    gpsControl.style.opacity = '0';
                    gpsControl.style.pointerEvents = 'none';
                }
            } else {
                setTimeout(arguments.callee, 1000);
            }
        }, 3000);
        
        function seguirUbicacionSiempre() {
            if (navigator.geolocation) {
                var options = {
                    enableHighAccuracy: true,
                    maximumAge: 10000,
                    timeout: 5000
                };
                
                navigator.geolocation.watchPosition(
                    function(position) {
                        console.log("📍 Ubicación actualizada");
                    },
                    function(error) {
                        console.log("⚠️ Error GPS:", error.message);
                    },
                    options
                );
            }
        }
        
        if (typeof map !== 'undefined') {
            map.on('locationfound', function(e) {
                console.log("📍 GPS activado con éxito");
                seguirUbicacionSiempre();
            });
        }
        </script>
        '''
        
        agregar_elemento_html_seguro(m, gps_auto_html)
        
    except Exception as e:
        print(f"⚠️  Error GPS: {e}")

    # ========== TÍTULO PRINCIPAL (100% IDÉNTICO) ==========
    # Obtener hora Argentina (UTC-3)
    from datetime import datetime, timezone, timedelta
    hora_argentina = datetime.now(timezone(timedelta(hours=-3)))
    fecha_hora_argentina = hora_argentina.strftime("%d/%m/%Y • %H:%M")
    
    titulo_html = f'''
    <div style="position: fixed;
            top: 8px; left: 8px;
            background: linear-gradient(135deg, #2C5530, #8A9A5B);
            padding: 6px 10px;
            border-radius: 8px;
            z-index: 9999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 10px;
            box-shadow: 0 3px 10px rgba(44, 85, 48, 0.3);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);">
        
        <div style="font-weight: 800; color: white; font-size: 12px; letter-spacing: -0.2px;">
            PROGRAMA CÓRDOBA 25/26
        </div>
        <div style="font-size: 9px; color: rgba(255, 255, 255, 0.9); margin-top: 1px;">
            Actualizado: {fecha_hora_argentina}
        </div>
    </div>
    '''
    agregar_elemento_html_seguro(m, titulo_html)

    # ========== LEYENDA DE CULTIVOS (100% IDÉNTICA) ==========
    if campos['cultivo'] and campos['hectareas']:
        gdf[campos['hectareas']] = pd.to_numeric(gdf[campos['hectareas']], errors='coerce').fillna(0)
        
        superficie_por_cultivo = {}
        for cultivo in gdf[campos['cultivo']].dropna().unique():
            mascara = gdf[campos['cultivo']] == cultivo
            hectareas = gdf.loc[mascara, campos['hectareas']].sum()
            superficie_por_cultivo[cultivo] = hectareas
        
        total_superficie = sum(superficie_por_cultivo.values())
        
        hectareas_soja = 0
        hectareas_maiz = 0
        
        for cultivo, hectareas in superficie_por_cultivo.items():
            cultivo_str = str(cultivo).lower()
            if 'soja' in cultivo_str or 'soya' in cultivo_str:
                hectareas_soja += hectareas
            elif 'maíz' in cultivo_str or 'maiz' in cultivo_str or 'corn' in cultivo_str:
                hectareas_maiz += hectareas
        
        items_leyenda = []
        
        if hectareas_soja > 0:
            items_leyenda.append(
                f'<div style="display: flex; align-items: center; margin-bottom: 6px; padding: 6px; border-radius: 6px; background: rgba(76, 175, 80, 0.1);">'
                f'<div style="display: flex; align-items: center; justify-content: center; width: 24px; height: 24px; background: #4CAF50; margin-right: 8px; border-radius: 6px; flex-shrink: 0;">'
                f'<span style="color: white; font-size: 10px;">🟢</span>'
                f'</div>'
                f'<div style="flex: 1;">'
                f'<div style="font-size: 10px; font-weight: 700; color: #2C2C2C;">SOJA</div>'
                f'<div style="font-size: 11px; font-weight: 800; color: #2C5530;">{hectareas_soja:,.0f} ha</div>'
                f'</div>'
                f'</div>'
            )
        
        if hectareas_maiz > 0:
            items_leyenda.append(
                f'<div style="display: flex; align-items: center; margin-bottom: 6px; padding: 6px; border-radius: 6px; background: rgba(255, 193, 7, 0.1);">'
                f'<div style="display: flex; align-items: center; justify-content: center; width: 24px; height: 24px; background: #FFC107; margin-right: 8px; border-radius: 6px; flex-shrink: 0;">'
                f'<span style="color: white; font-size: 10px;">🟡</span>'
                f'</div>'
                f'<div style="flex: 1;">'
                f'<div style="font-size: 10px; font-weight: 700; color: #2C2C2C;">MAÍZ</div>'
                f'<div style="font-size: 11px; font-weight: 800; color: #2C5530;">{hectareas_maiz:,.0f} ha</div>'
                f'</div>'
                f'</div>'
            )
        
        items_leyenda.append(
            f'<div style="margin-top: 8px; padding: 8px; background: linear-gradient(135deg, #2C5530, #8A9A5B); border-radius: 8px;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; font-size: 10px;">'
            f'<div style="font-weight: 700; color: white;">TOTAL</div>'
            f'<div style="font-size: 12px; font-weight: 800; color: white;">{total_superficie:,.0f} ha</div>'
            f'</div>'
            f'</div>'
        )

        leyenda_html = f'''
        <div style="position: fixed;
                bottom: 8px; right: 8px;
                background: white;
                padding: 10px;
                border-radius: 10px;
                border: 1px solid rgba(212, 212, 212, 0.8);
                z-index: 9999;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 11px;
                width: 160px;
                max-height: 250px;
                overflow-y: auto;
                box-shadow: 0 3px 15px rgba(44, 85, 48, 0.15);">
            
            {"".join(items_leyenda)}
        </div>
        '''

        agregar_elemento_html_seguro(m, leyenda_html)

    # ========== BUSCADOR DE CLIENTES (100% IDÉNTICO) ==========
    if campos['cliente']:
        clientes = sorted(gdf[campos['cliente']].dropna().astype(str).unique())
        
        opciones_clientes = "".join(f'<option value="{cliente}">' for cliente in clientes)
        
        buscador_html = f'''
        <div id="lupitaBuscador" style="position: fixed;
                top: 80px; left: 8px;
                background: linear-gradient(135deg, rgba(250, 249, 246, 0.95) 0%, rgba(245, 245, 240, 0.95) 100%);
                padding: 10px 12px;
                border-radius: 12px;
                border: 1px solid rgba(212, 212, 212, 0.8);
                z-index: 9998;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 11px;
                width: 220px;
                box-shadow: 0 5px 20px rgba(44, 85, 48, 0.12);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);">

            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <div style="width: 28px; height: 28px; background: linear-gradient(135deg, #2C5530, #8A9A5B);
                            border-radius: 6px; display: flex; align-items: center; justify-content: center;">
                        <span style="color: white; font-size: 12px;">🔍</span>
                    </div>
                    <div style="font-weight: 700; color: #2C5530; font-size: 12px;">
                        Buscar cliente
                    </div>
                </div>
                <button id="toggleBuscador"
                        style="background: rgba(44, 85, 48, 0.1); 
                               border: none; 
                               cursor: pointer; 
                               font-size: 14px; 
                               color: #2C5530;
                               width: 24px;
                               height: 24px;
                               border-radius: 6px;
                               display: flex;
                               align-items: center;
                               justify-content: center;"
                        onclick="toggleBuscador()">↻</button>
            </div>

            <div id="contenidoBuscador">
            
                <!-- ========== SISTEMA DE DETECCIÓN AUTOMÁTICA ========== -->
                <script>
                // FUNCIÓN PARA ENCONTRAR EL MAPA (aunque cambie el nombre)
                function obtenerMapaSeguro() {{
                    // Si ya lo encontramos, reusar
                    if (window._miMapa && window._miMapa.fitBounds) {{
                        return window._miMapa;
                    }}
                    
                    // Buscar en ventana global
                    for (var key in window) {{
                        try {{
                            var obj = window[key];
                            // Características únicas de mapa Leaflet
                            if (obj && 
                                typeof obj.fitBounds === 'function' &&
                                typeof obj.setView === 'function' && 
                                typeof obj.getBounds === 'function' &&
                                obj._container && obj._container.tagName === 'DIV') {{
                                
                                console.log("🗺️ Mapa detectado automáticamente:", key);
                                window._miMapa = obj;  // Guardar para siempre
                                window.map = obj;      // Compatibilidad
                                return obj;
                            }}
                        }} catch(e) {{}}
                    }}
                    
                    console.error("❌ No se pudo encontrar el mapa");
                    return null;
                }}
                
                // FUNCIÓN PARA ENCONTRAR CAPA DE POLÍGONOS
                function obtenerCapaPoligonosSegura() {{
                    // Primero, buscar por nombre específico (si ya sabemos cómo se llama)
                    if (window._miCapaPoligonos && window._miCapaPoligonos.eachLayer) {{
                        return window._miCapaPoligonos;
                    }}
                    
                    // Buscar en el mapa directamente (si ya tenemos el mapa)
                    var mapa = obtenerMapaSeguro();
                    if (mapa) {{
                        // Buscar entre todas las capas del mapa
                        for (var key in mapa._layers) {{
                            var layer = mapa._layers[key];
                            if (layer && typeof layer.eachLayer === 'function') {{
                                var contador = 0;
                                try {{
                                    layer.eachLayer(function() {{ contador++; }});
                                    if (contador > 1000) {{  // Si tiene más de 1000 polígonos
                                        console.log("✅ Capa principal encontrada en mapa:", contador, "polígonos");
                                        window._miCapaPoligonos = layer;
                                        return layer;
                                    }}
                                }} catch(e) {{}}
                            }}
                        }}
                    }}
                    
                    // Si no encontramos, buscar en ventana global como antes
                    for (var key in window) {{
                        try {{
                            var obj = window[key];
                            if (obj && typeof obj.eachLayer === 'function') {{
                                var contador = 0;
                                obj.eachLayer(function() {{ contador++; }});
                                
                                if (contador > 5000) {{  // Tu capa tiene ~5700
                                    console.log("✅ Capa principal detectada en window:", key, "(" + contador + " polígonos)");
                                    window._miCapaPoligonos = obj;
                                    return obj;
                                }}
                            }}
                        }} catch(e) {{}}
                    }}
                    
                    // Fallback: buscar geo_json_
                    for (var key in window) {{
                        if (key.startsWith('geo_json_')) {{
                            console.log("⚠️ Usando fallback:", key);
                            return window[key];
                        }}
                    }}
                    
                    console.error("❌ No se pudo encontrar ninguna capa de polígonos");
                    return null;
                }}
                
                // INICIALIZAR AL CARGAR
                setTimeout(function() {{
                    obtenerMapaSeguro();
                    obtenerCapaPoligonosSegura();
                    console.log("✅ Sistema de detección listo");
                }}, 500);
                </script>
                <!-- ========== FIN DETECCIÓN ========== -->
                
                <div style="margin-bottom: 10px;">
                    <input list="clientesList"
                           id="clienteInput"
                           placeholder="🔍 Escribe o selecciona cliente..."
                           style="width: 100%; 
                                  padding: 8px 10px;
                                  border: 2px solid rgba(212, 212, 212, 0.8);
                                  border-radius: 8px;
                                  font-size: 11px;
                                  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                                  background: white;
                                  color: #2C2C2C;">
                    <datalist id="clientesList">
                        {opciones_clientes}
                    </datalist>
                </div>

                <div style="display: flex; gap: 6px; margin-bottom: 8px;">
                    <button onclick="filtrarCliente()"
                            style="flex: 1; 
                                   background: linear-gradient(135deg, #2C5530, #8A9A5B);
                                   color: white;
                                   border: none;
                                   padding: 8px;
                                   border-radius: 8px;
                                   cursor: pointer;
                                   font-size: 10px;
                                   font-weight: 600;">
                        <span>✓</span>
                        <span>Filtrar</span>
                    </button>
    
                    <button onclick="resetearFiltro()"
                            style="flex: 1; 
                                   background: linear-gradient(135deg, #FAF9F6, #F5F5F0);
                                   color: #666;
                                   border: 2px solid rgba(212, 212, 212, 0.8);
                                   padding: 8px;
                                   border-radius: 8px;
                                   cursor: pointer;
                                   font-size: 10px;
                                   font-weight: 600;">
                        <span>↺</span>
                        <span>Resetear</span>
                    </button>
                </div>

                <div id="estadoFiltro"
                     style="font-size: 9px; 
                            color: #666; 
                            margin-top: 10px;
                            padding: 8px;
                            background: rgba(44, 85, 48, 0.05);
                            border-radius: 6px;
                            border-left: 4px solid #8A9A5B;
                            display: flex;
                            align-items: center;
                            gap: 6px;">
                    <div style="width: 6px; height: 6px; background: #2C5530; border-radius: 50%;"></div>
                    <div>Mostrando <span style="font-weight: 700; color: #2C5530;">{len(gdf)}</span> polígonos</div>
                </div>
            </div>
        </div>

        <script>
        // Variables globales - EXACTO A COLAB
        var boundsGeneral = null;
        var contenidoVisible = true;
        var mapaPoligonos = new Map();

        // Función para mostrar/ocultar contenido - CON BOTÓN ↻/▼
        function toggleBuscador() {{
            var contenido = document.getElementById("contenidoBuscador");
            var toggleBtn = document.getElementById("toggleBuscador");
            var lupita = document.getElementById("lupitaBuscador");

            if (contenidoVisible) {{
                contenido.style.display = "none";
                toggleBtn.innerHTML = "▼";
                lupita.style.width = "140px";
                lupita.style.padding = "6px 8px";
            }} else {{
                contenido.style.display = "block";
                toggleBtn.innerHTML = "↻";
                lupita.style.width = "220px";
                lupita.style.padding = "10px 12px";
            }}
            contenidoVisible = !contenidoVisible;
        }}

        // Almacenar referencia a cada polígono al inicio
        function inicializarPoligonos() {{
            var capa = obtenerCapaPoligonosSegura();
            if (capa) {{
                capa.eachLayer(function(layer) {{
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
        }}

        // ========== SISTEMA DE FILTRADO AVANZADO CORREGIDO ==========

        // Variables globales
        var capaOriginal = null;
        var capaFiltrada = null;

        function filtrarCliente() {{
            console.log("🔍 Iniciando búsqueda avanzada...");

            var mapa = obtenerMapaSeguro();
            var capa = obtenerCapaPoligonosSegura();

            if (!mapa || !capa) {{
                alert("❌ Error: No se pudo inicializar el sistema.");
                return;
            }}

            var valor = document.getElementById("clienteInput").value.toLowerCase();
            if (!valor) {{
                alert("Por favor, escribe o selecciona un cliente");
                return;
            }}
        
            // Guardar referencia a la capa original (solo primera vez)
            if (!capaOriginal) {{
                capaOriginal = capa;
            }}
        
            // Limpiar filtro anterior
            if (capaFiltrada) {{
                mapa.removeLayer(capaFiltrada);
                capaFiltrada = null;
            }}
        
            var boundsFiltrados = null;
            var featuresFiltrados = [];
            var contadorFiltrados = 0;

            console.log("🔍 Buscando coincidencias...");

            // 1. DESHABILITAR TODOS los polígonos primero
            capaOriginal.eachLayer(function(layer) {{
                // OCULTAR COMPLETAMENTE
                layer.setStyle({{
                    fillOpacity: 0,
                    weight: 0,
                    opacity: 0
                }});
                
                // DESHABILITAR INTERACTIVIDAD
                layer.options.interactive = false;
                
                // Remover tooltip temporalmente
                if (layer._tooltip) {{
                    layer.unbindTooltip();
                }}
                
                // Remover popup temporalmente (pero guardar que tenía popup)
                if (layer._popup) {{
                    layer._teniaPopup = true;
                    layer.unbindPopup();
                }}
                
                // Remover eventos de mouse
                layer.off('mouseover');
                layer.off('mouseout');
                layer.off('click');
                
                // Verificar si coincide con la búsqueda
                var propiedades = layer.feature.properties;
                var clienteEnPoligono = propiedades["{campos['cliente']}"];

                if (clienteEnPoligono && clienteEnPoligono.toString().toLowerCase().includes(valor)) {{
                    // Agregar a la lista de filtrados
                    featuresFiltrados.push(layer.feature);
                    contadorFiltrados++;

                    // Para zoom
                    var layerBounds = layer.getBounds();
                    if (layerBounds && layerBounds.isValid()) {{
                        boundsFiltrados = boundsFiltrados ? boundsFiltrados.extend(layerBounds) : layerBounds;
                    }}
                }}
            }});
        
            console.log("✅ Encontrados:", contadorFiltrados, "polígonos");

            // 2. CREAR nueva capa SOLO con los filtrados - CORREGIDO
            if (featuresFiltrados.length > 0) {{
                var geoJsonFiltrado = {{
                    type: "FeatureCollection",
                    features: featuresFiltrados
                }};

                capaFiltrada = L.geoJSON(geoJsonFiltrado, {{
                    style: function(feature) {{
                        return {{
                            fillColor: feature.properties._color_fill || '#9C27B0',
                            color: feature.properties._color_border || '#7B1FA2',
                            weight: 2,
                            fillOpacity: 0.6,
                            opacity: 1
                        }};
                    }},
                    onEachFeature: function(feature, layer) {{
                        // ACTIVAR interactividad SOLO para filtrados
                        layer.options.interactive = true;
                        layer.options.bubblingMouseEvents = true; // IMPORTANTE: Permitir eventos
                        
                        // Restaurar tooltip
                        if (feature.properties["{campos['cliente']}"]) {{
                            layer.bindTooltip(feature.properties["{campos['cliente']}"], {{
                                sticky: true,
                                className: 'leaflet-tooltip-custom'
                            }});
                        }}
                        
                        // CREAR POPUP NUEVO - FIX CRÍTICO: Usar el popup EXACTO que debería tener
                        var popupContent = crearContenidoPopup(feature.properties);
                        
                        layer.bindPopup(popupContent, {{
                            maxWidth: 350,
                            minWidth: 250,
                            className: 'leaflet-popup-custom'
                        }});
                        
                        // Agregar eventos de hover
                        layer.on('mouseover', function(e) {{
                            e.target.setStyle({{
                                fillOpacity: 0.8,
                                weight: 3
                            }});
                        }});
                        
                        layer.on('mouseout', function(e) {{
                            e.target.setStyle({{
                                fillOpacity: 0.6,
                                weight: 2
                            }});
                        }});
                        
                        // Evento click para abrir popup
                        layer.on('click', function(e) {{
                            // Esto es CRÍTICO: Abrir el popup programáticamente si no se abre solo
                            layer.openPopup();
                        }});
                    }}
                }}).addTo(mapa);
        
                // 3. ZOOM a los filtrados
                if (boundsFiltrados && boundsFiltrados.isValid()) {{
                    console.log("🎯 Haciendo zoom a bounds filtrados");
                    mapa.fitBounds(boundsFiltrados, {{
                        padding: [80, 80],
                        duration: 1,
                        maxZoom: 15
                    }});
                }}
            }}
        
            // 4. ACTUALIZAR ESTADO
            var estadoDiv = document.getElementById("estadoFiltro");
            if (contadorFiltrados > 0) {{
                estadoDiv.innerHTML = "Mostrando " + contadorFiltrados + " polígonos";
                estadoDiv.style.color = "#4CAF50";
            }} else {{
                estadoDiv.innerHTML = "❌ No se encontraron resultados";
                estadoDiv.style.color = "#f44336";
            }}
        }}

        // FUNCIÓN PARA CREAR CONTENIDO DEL POPUP (idéntico al original)
        function crearContenidoPopup(propiedades) {{
            var props = propiedades || {{}};
            
            // Crear HTML del popup (igual que en tu aplicación original)
            var popupContent = '<div style="font-family: Arial, sans-serif; font-size: 11px; max-width: 350px; max-height: 400px; overflow-y: auto; padding: 10px;">';
            
            // Agregar campos importantes
            var camposParaPopup = [
                'CUIT', 'CLIENTE', 'CAMPO', 'DEPARTAMENTO', 'LOCALIDAD', 
                'CULTIVO', 'LOTE', 'HECTAREAS_DECLARADAS', 'HECTAREAS_ASEGURADAS',
                'ZONA_CZ4', 'RENDIMIENTO_ASEGURADO', 'SUMA_ASEGURADA', 'FECHA_SIEMBRA'
            ];
            
            for (var i = 0; i < camposParaPopup.length; i++) {{
                var campo = camposParaPopup[i];
                if (props[campo] !== undefined && props[campo] !== null && props[campo] !== '') {{
                    popupContent += '<div style="margin-bottom: 8px;">';
                    popupContent += '<strong style="color: #2C5530;">' + campo + ':</strong> ';
                    popupContent += '<span style="color: #333;">' + props[campo] + '</span>';
                    popupContent += '</div>';
                }}
            }}
            
            // Agregar campo del cliente (si existe y no está ya)
            var campoCliente = "{campos['cliente']}";
            if (campoCliente && props[campoCliente] && !camposParaPopup.includes(campoCliente)) {{
                popupContent += '<div style="margin-bottom: 8px;">';
                popupContent += '<strong style="color: #2C5530;">CLIENTE:</strong> ';
                popupContent += '<span style="color: #333;">' + props[campoCliente] + '</span>';
                popupContent += '</div>';
            }}
            
            popupContent += '</div>';
            
            return popupContent;
        }}

        function resetearFiltro() {{
            console.log("🔄 Restableciendo filtro avanzado...");
            
            var mapa = obtenerMapaSeguro();
            
            if (!mapa || !capaOriginal) {{
                console.error("❌ No se pudo restablecer");
                return;
            }}
        
            // 1. Limpiar input
            document.getElementById("clienteInput").value = "";

            // 2. ELIMINAR capa filtrada si existe
            if (capaFiltrada) {{
                mapa.removeLayer(capaFiltrada);
                capaFiltrada = null;
            }}
        
            // 3. RESTAURAR TODOS los polígonos individualmente
            capaOriginal.eachLayer(function(layer) {{
                // Restaurar estilo
                layer.setStyle({{
                    fillColor: layer.feature.properties._color_fill || '#9C27B0',
                    color: layer.feature.properties._color_border || '#7B1FA2',
                    weight: 2,
                    fillOpacity: 0.6,
                    opacity: 1
                }});
                
                // RESTAURAR interactividad COMPLETA
                layer.options.interactive = true;
                layer.options.bubblingMouseEvents = true;
                
                // Restaurar tooltip
                if (layer.feature.properties["{campos['cliente']}"]) {{
                    layer.bindTooltip(layer.feature.properties["{campos['cliente']}"], {{
                        sticky: true,
                        className: 'leaflet-tooltip-custom'
                    }});
                }}
                
                // Restaurar popup usando la misma función
                var popupContent = crearContenidoPopup(layer.feature.properties);
                layer.bindPopup(popupContent, {{
                    maxWidth: 350,
                    minWidth: 250,
                    className: 'leaflet-popup-custom'
                }});
                
                // Restaurar eventos de hover
                layer.on('mouseover', function(e) {{
                    e.target.setStyle({{
                        fillOpacity: 0.8,
                        weight: 3
                    }});
                }});
                
                layer.on('mouseout', function(e) {{
                    e.target.setStyle({{
                        fillOpacity: 0.6,
                        weight: 2
                    }});
                }});
            }});

            // 4. RESTAURAR ZOOM original
            var boundsGeneral = capaOriginal.getBounds();
            if (boundsGeneral && boundsGeneral.isValid()) {{
                console.log("📍 Restaurando zoom original...");
                mapa.fitBounds(boundsGeneral, {{padding: [50, 50]}});
            }}
        
            // 5. ACTUALIZAR ESTADO
            var estadoDiv = document.getElementById("estadoFiltro");
            var contadorTotal = 0;
            capaOriginal.eachLayer(function() {{ contadorTotal++; }});
            estadoDiv.innerHTML = "Mostrando todos (" + contadorTotal + ")";
            estadoDiv.style.color = "#666";
            
            console.log("✅ Filtro restablecido completamente");
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
        
        agregar_elemento_html_seguro(m, buscador_html)

    # ========== PANEL DE COMPARACIÓN POR ZONA (100% IDÉNTICO) ==========
    if campos['zona'] and campos['hectareas']:
        gdf[campos['zona']] = gdf[campos['zona']].astype(str).str.strip()
        hectareas_por_zona = {}
        for zona in gdf[campos['zona']].dropna().unique():
            zona_str = str(zona).strip()
            mascara = gdf[campos['zona']] == zona_str
            hectareas = gdf.loc[mascara, campos['hectareas']].sum()
            hectareas_por_zona[zona_str] = hectareas
        
        # Hectáreas proyectadas por zona (EXACTAMENTE COMO EN COLAB)
        hectareas_proyectadas = {
            "1": 128998,
            "2": 65245,
            "3": 187636,
            "4": 151566
        }
        
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
        
        max_valor = max(max(datos_proyectados), max(datos_reales)) if datos_proyectados and datos_reales else 100000
        
        panel_graficos_html = f'''

        <!-- BOTÓN FLOTANTE MÁS PEQUEÑO - EXACTO A COLAB -->
        <div id="btnGraficos" style="position: fixed;
                bottom: 25px; left: 25px;
                background: linear-gradient(135deg, #2C5530, #8A9A5B);
                color: white;
                padding: 12px;
                border-radius: 50%;
                z-index: 9997;
                cursor: pointer;
                box-shadow: 0 5px 15px rgba(44, 85, 48, 0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 20px;
                width: 50px;
                height: 50px;
                transition: all 0.3s;"
                onclick="togglePanelGraficos()"
                onmouseover="this.style.transform='scale(1.1)'; this.style.boxShadow='0 8px 25px rgba(44, 85, 48, 0.4)';"
                onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 5px 15px rgba(44, 85, 48, 0.3)';">
            <div style="display: flex; align-items: center; justify-content: center; width: 100%; height: 100%;">
                📈
            </div>
        </div>

        <!-- PANEL DESPLEGABLE DE GRÁFICOS - MÁS PEQUEÑO - EXACTO -->
        <div id="panelGraficos" style="position: fixed;
                bottom: -80%;
                left: 0;
                width: 100%;
                height: 80%;
                background-color: white;
                z-index: 10001;
                box-shadow: 0 -3px 15px rgba(0,0,0,0.3);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                transition: bottom 0.4s ease;
                overflow-y: auto;
                font-family: Arial, sans-serif;">

            <!-- CABECERA DEL PANEL - EXACTA -->
            <div style="position: sticky; top: 0; background: linear-gradient(135deg, #2C5530, #8A9A5B); color: white;
                    padding: 15px 20px; border-top-left-radius: 12px; border-top-right-radius: 12px;
                    display: flex; justify-content: space-between; align-items: center; z-index: 1;
                    box-shadow: 0 3px 15px rgba(44, 85, 48, 0.3);">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 36px; height: 36px; background: rgba(255, 255, 255, 0.2); 
                            border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                        <span style="font-size: 18px;">📊</span>
                    </div>
                    <div>
                        <div style="font-size: 16px; font-weight: 700; color: white;">
                            COMPARACIÓN POR ZONA
                        </div>
                        <div style="font-size: 11px; color: rgba(255, 255, 255, 0.9); margin-top: 2px;">
                            Proyectado vs Actual - Campaña 25/26
                        </div>
                    </div>
                </div>
                <button onclick="togglePanelGraficos()"
                        style="background: rgba(255, 255, 255, 0.2); 
                               border: none; 
                               color: white; 
                               font-size: 22px;
                               cursor: pointer; 
                               padding: 0; 
                               width: 32px; 
                               height: 32px;
                               border-radius: 8px;
                               display: flex;
                               align-items: center;
                               justify-content: center;">
                    ×
                </button>
            </div>
            
            <!-- CONTENIDO DEL PANEL - EXACTO -->
            <div style="padding: 15px; max-width: 900px; margin: 0 auto;">

                <!-- RESUMEN - EXACTO -->
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                            gap: 12px; margin-bottom: 20px;">
                    <div style="background-color: #f8f9fa; padding: 12px; border-radius: 6px; border-left: 4px solid #2E7D32;">
                        <div style="font-size: 11px; color: #666; margin-bottom: 5px;">TOTAL PROYECTADO</div>
                        <div style="font-size: 20px; font-weight: bold; color: #2E7D32;">
                            {sum(hectareas_proyectadas.values()):,.0f} ha
                        </div>
                    </div>
                    <div style="background-color: #f8f9fa; padding: 12px; border-radius: 6px; border-left: 4px solid #2196F3;">
                        <div style="font-size: 11px; color: #666; margin-bottom: 5px;">TOTAL ACTUAL</div>
                        <div style="font-size: 20px; font-weight: bold; color: #2196F3;">
                            {sum(hectareas_por_zona.values()):,.0f} ha
                        </div>
                    </div>
                    <div style="background-color: #f8f9fa; padding: 12px; border-radius: 6px; border-left: 4px solid #FF9800;">
                        <div style="font-size: 11px; color: #666; margin-bottom: 5px;">DIFERENCIA TOTAL</div>
                        <div style="font-size: 20px; font-weight: bold; color: {'red' if (sum(hectareas_por_zona.values()) - sum(hectareas_proyectadas.values())) < 0 else '#4CAF50'};">
                            {sum(hectareas_por_zona.values()) - sum(hectareas_proyectadas.values()):+,.0f} ha
                        </div>
                    </div>
                    <div style="background-color: #f8f9fa; padding: 12px; border-radius: 6px; border-left: 4px solid #9C27B0;">
                        <div style="font-size: 11px; color: #666; margin-bottom: 5px;">% DE CUMPLIMIENTO</div>
                        <div style="font-size: 20px; font-weight: bold; color: {'red' if ((sum(hectareas_por_zona.values()) / sum(hectareas_proyectadas.values()) * 100) if sum(hectareas_proyectadas.values()) > 0 else 0) < 100 else '#4CAF50'};">
                            {(sum(hectareas_por_zona.values()) / sum(hectareas_proyectadas.values()) * 100) if sum(hectareas_proyectadas.values()) > 0 else 0:.1f}%
                        </div>
                    </div>
                </div>

                <!-- GRÁFICO DE BARRAS AGRUPADAS - EXACTO -->
                <div style="background-color: white; border: 1px solid #e0e0e0; border-radius: 8px;
                            padding: 15px; margin-bottom: 20px;">
                    <h3 style="margin-top: 0; margin-bottom: 15px; color: #333; font-size: 15px;
                              border-bottom: 2px solid #2E7D32; padding-bottom: 6px;">
                        HECTÁREAS POR ZONA - COMPARACIÓN
                    </h3>

                    <div style="display: flex; flex-direction: column; gap: 15px;">
        '''
        
        for i, zona in enumerate(zonas_ordenadas):
            proyectado = datos_proyectados[i]
            real = datos_reales[i]
            diferencia = diferencias[i]
            porcentaje = porcentajes_dif[i]
            
            ancho_proyectado = min(95, (proyectado / max_valor * 95))
            ancho_real = min(95, (real / max_valor * 95))
            
            color_proyectado = "#2E7D32"
            color_real = "#2196F3" if diferencia >= 0 else "#f44336"
            color_diferencia = "#4CAF50" if diferencia >= 0 else "#f44336"
            icono_diferencia = "↗️" if diferencia >= 0 else "↘️"
            
            panel_graficos_html += f'''
                        <!-- ZONA {zona} - EXACTO -->
                        <div style="margin-bottom: 8px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                                <div style="font-weight: bold; color: #333; font-size: 13px;">
                                    ZONA {zona}
                                </div>
                                <div style="font-size: 12px; color: #666;">
                                    Diferencia: <span style="font-weight: bold; color: {color_diferencia}">
                                        {diferencia:+,.0f} ha ({porcentaje:+.1f}%) {icono_diferencia}
                                    </span>
                                </div>
                            </div>

                            <div style="margin-bottom: 8px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                                    <span style="font-size: 11px; color: #666;">Proyectado</span>
                                    <span style="font-size: 11px; font-weight: bold; color: {color_proyectado}">
                                        {proyectado:,.0f} ha
                                    </span>
                                </div>
                                <div style="width: 100%; background-color: #f0f0f0; border-radius: 4px; height: 20px; overflow: hidden;">
                                    <div style="width: {ancho_proyectado}%; height: 100%; background-color: {color_proyectado};
                                            border-radius: 4px; display: flex; align-items: center; padding-left: 8px;">
                                        <span style="color: white; font-size: 10px; font-weight: bold;">
                                            PROYECTADO
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div style="margin-bottom: 12px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                                    <span style="font-size: 11px; color: #666;">Actual</span>
                                    <span style="font-size: 11px; font-weight: bold; color: {color_real}">
                                        {real:,.0f} ha
                                    </span>
                                </div>
                                <div style="width: 100%; background-color: #f0f0f0; border-radius: 4px; height: 20px; overflow: hidden;">
                                    <div style="width: {ancho_real}%; height: 100%; background-color: {color_real};
                                            border-radius: 4px; display: flex; align-items: center; padding-left: 8px;">
                                        <span style="color: white; font-size: 10px; font-weight: bold;">
                                            ACTUAL
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
            '''
        
        panel_graficos_html += '''
                    </div>
                </div>
                
                <!-- TABLA RESUMEN - EXACTA -->
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                        <thead>
                            <tr style="background-color: #f5f5f5;">
                                <th style="padding: 8px; text-align: left; border-bottom: 2px solid #2E7D32;">ZONA</th>
                                <th style="padding: 8px; text-align: right; border-bottom: 2px solid #2E7D32;">PROYECTADO (ha)</th>
                                <th style="padding: 8px; text-align: right; border-bottom: 2px solid #2E7D32;">ACTUAL (ha)</th>
                                <th style="padding: 8px; text-align: right; border-bottom: 2px solid #2E7D32;">DIFERENCIA (ha)</th>
                                <th style="padding: 8px; text-align: right; border-bottom: 2px solid #2E7D32;">DIFERENCIA (%)</th>
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
                                <td style="padding: 8px; font-weight: bold;">Zona {zona}</td>
                                <td style="padding: 8px; text-align: right;">{proyectado:,.0f}</td>
                                <td style="padding: 8px; text-align: right; font-weight: bold;">{real:,.0f}</td>
                                <td style="padding: 8px; text-align: right; color: {color_diferencia}; font-weight: bold;">
                                    {diferencia:+,.0f}
                                </td>
                                <td style="padding: 8px; text-align: right; color: {color_diferencia};">
                                    {porcentaje:+.1f}%
                                </td>
                            </tr>
            '''
        
        panel_graficos_html += f'''
                        </tbody>
                        <tfoot style="background-color: #f9f9f9; font-weight: bold;">
                            <tr>
                                <td style="padding: 8px; border-top: 2px solid #2E7D32;">TOTAL</td>
                                <td style="padding: 8px; text-align: right; border-top: 2px solid #2E7D32;">
                                    {sum(datos_proyectados):,.0f}
                                </td>
                                <td style="padding: 8px; text-align: right; border-top: 2px solid #2E7D32;">
                                    {sum(datos_reales):,.0f}
                                </td>
                                <td style="padding: 8px; text-align: right; border-top: 2px solid #2E7D32;
                                    color: {'#4CAF50' if (sum(datos_reales) - sum(datos_proyectados)) >= 0 else '#f44336'};">
                                    {sum(datos_reales) - sum(datos_proyectados):+,.0f}
                                </td>
                                <td style="padding: 8px; text-align: right; border-top: 2px solid #2E7D32;
                                    color: {'#4CAF50' if ((sum(datos_reales) / sum(datos_proyectados) * 100) - 100 if sum(datos_proyectados) > 0 else 0) >= 0 else '#f44336'};">
                                    {((sum(datos_reales) / sum(datos_proyectados) * 100) - 100) if sum(datos_proyectados) > 0 else 0:+.1f}%
                                </td>
                            </tr>
                        </tfoot>
                    </table>
                </div>

                <!-- INFORMACIÓN ADICIONAL - EXACTA -->
                <div style="font-size: 11px; color: #666; padding: 12px; background-color: #f8f9fa;
                            border-radius: 6px; border-left: 4px solid #FF9800;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                        <span>💡</span>
                        <strong>Información para el análisis:</strong>
                    </div>
                    <ul style="margin: 0; padding-left: 18px;">
                        <li>Datos proyectados: valores estimados para la campaña 25/26</li>
                        <li>Datos actuales: calculados automáticamente del archivo GeoJSON cargado</li>
                        <li>Verde (↑): la zona supera la proyección</li>
                        <li>Rojo (↓): la zona está por debajo de la proyección</li>
                        <li>Actualizado: {hora_argentina.strftime("%d/%m/%Y %H:%M")}</li>
                    </ul>
                </div>

            </div>
        </div>

        <script>
        let panelAbierto = false;

        function togglePanelGraficos() {{
            const panel = document.getElementById("panelGraficos");
            const btn = document.getElementById("btnGraficos");

            if (panelAbierto) {{
                // Cerrar panel
                panel.style.bottom = "-80%";
                panel.style.zIndex = "9998";
                btn.innerHTML = "📈";

            }} else {{
                // Abrir panel
                panel.style.zIndex = "10001";
                panel.style.bottom = "0";
                btn.innerHTML = "📊";
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

        // Ocultar botón hasta después del login
        document.addEventListener('DOMContentLoaded', function() {{
            document.getElementById("btnGraficos").style.display = "none";
        }});
        </script>
        '''
        
        agregar_elemento_html_seguro(m, panel_graficos_html)

    # ========== ESTILOS GLOBALES (100% IDÉNTICOS) ==========
    estilos_globales = '''
    <style>
        :root {
            --color-fondo: #FAF9F6;
            --color-primario: #2C5530;
            --color-secundario: #8A9A5B;
            --color-accento: #B8860B;
            --color-texto: #2C2C2C;
            --color-borde: rgba(212, 212, 212, 0.8);
            --color-sombra: rgba(44, 85, 48, 0.1);
        }
    
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
    
        ::-webkit-scrollbar-track {
            background: rgba(250, 249, 246, 0.8);
            border-radius: 8px;
        }
    
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #2C5530, #8A9A5B);
            border-radius: 8px;
        }
    
        .leaflet-tooltip {
            background: linear-gradient(135deg, rgba(250, 249, 246, 0.95), rgba(245, 245, 240, 0.95));
            border: 1px solid rgba(212, 212, 212, 0.8);
            border-radius: 6px;
            padding: 6px 10px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 10px;
            color: #2C2C2C;
            box-shadow: 0 3px 10px rgba(44, 85, 48, 0.1);
        }
    
        .leaflet-popup-content-wrapper {
            background: linear-gradient(135deg, rgba(250, 249, 246, 0.98), rgba(245, 245, 240, 0.98));
            border-radius: 10px;
            border: 1px solid rgba(212, 212, 212, 0.8);
            box-shadow: 0 6px 20px rgba(44, 85, 48, 0.15);
        }
    
        .leaflet-popup-content {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 11px;
            color: #2C2C2C;
        }
    
        .leaflet-control-zoom a {
            background: linear-gradient(135deg, rgba(250, 249, 246, 0.95), rgba(245, 245, 240, 0.95));
            border: 1px solid rgba(212, 212, 212, 0.8) !important;
            color: #2C5530 !important;
            border-radius: 6px !important;
        }
    
        .leaflet-control-layers {
            background: linear-gradient(135deg, rgba(250, 249, 246, 0.95), rgba(245, 245, 240, 0.95)) !important;
            border: 1px solid rgba(212, 212, 212, 0.8) !important;
            border-radius: 10px !important;
        }
    </style>
    '''
    
    agregar_elemento_html_seguro(m, estilos_globales)

    # ========== PANTALLA DE LOGIN (100% IDÉNTICA) ==========
    login_html = f'''
    <div id="loginScreen" style="position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: linear-gradient(135deg, #2C5530 0%, #8A9A5B 100%);
            z-index: 10000;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            transition: opacity 0.5s ease;">

        <div style="background: rgba(255, 255, 255, 0.95);
                    padding: 30px 25px;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    text-align: center;
                    max-width: 320px;
                    width: 90%;
                    backdrop-filter: blur(15px);
                    -webkit-backdrop-filter: blur(15px);">

            <!-- LOGO -->
            <div style="margin-bottom: 20px;">
                <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #2C5530, #8A9A5B);
                        border-radius: 15px; display: flex; align-items: center; justify-content: center;
                        margin: 0 auto 12px; box-shadow: 0 4px 15px rgba(44, 85, 48, 0.3);">
                    <span style="color: white; font-size: 28px;">🔐</span>
                </div>
                <h2 style="color: #2C5530; margin-bottom: 5px; font-weight: 800; font-size: 18px;">
                    PROGRAMA CÓRDOBA 25/26
                </h2>
            </div>

            <!-- FORMULARIO -->
            <div style="margin-bottom: 20px; text-align: left;">
                <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 6px; font-weight: 600; color: #2C5530; font-size: 12px;">
                        👤 Usuario
                    </label>
                    <input type="text" id="loginUsuario"
                           placeholder="Ingrese su usuario"
                           style="width: 100%; padding: 12px 14px;
                                  border: 2px solid rgba(212, 212, 212, 0.8);
                                  border-radius: 10px;
                                  font-size: 14px;
                                  background: white;
                                  color: #2C2C2C;
                                  box-sizing: border-box;"
                           onfocus="this.style.borderColor='#8A9A5B'; this.style.boxShadow='0 0 0 3px rgba(138, 154, 91, 0.2)';"
                           onblur="this.style.borderColor='rgba(212, 212, 212, 0.8)'; this.style.boxShadow='none';">
                </div>

                <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 6px; font-weight: 600; color: #2C5530; font-size: 12px;">
                        🔒 Contraseña
                    </label>
                    <input type="password" id="loginContrasena"
                           placeholder="Ingrese su contraseña"
                           style="width: 100%; padding: 12px 14px;
                                  border: 2px solid rgba(212, 212, 212, 0.8);
                                  border-radius: 10px;
                                  font-size: 14px;
                                  background: white;
                                  color: #2C2C2C;
                                  box-sizing: border-box;"
                           onfocus="this.style.borderColor='#8A9A5B'; this.style.boxShadow='0 0 0 3px rgba(138, 154, 91, 0.2)';"
                           onblur="this.style.borderColor='rgba(212, 212, 212, 0.8)'; this.style.boxShadow='none';">
                </div>

                <button onclick="verificarAcceso()"
                        style="width: 100%;
                               background: linear-gradient(135deg, #2C5530, #8A9A5B);
                               color: white;
                               border: none;
                               padding: 14px;
                               border-radius: 10px;
                               font-size: 15px;
                               font-weight: 700;
                               cursor: pointer;
                               transition: all 0.3s;
                               display: flex;
                               align-items: center;
                               justify-content: center;
                               gap: 8px;"
                        onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(44, 85, 48, 0.4)';"
                        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
                    <span>🔓</span>
                    <span>INGRESAR</span>
                </button>
            </div>

            <!-- MENSAJE DE ERROR -->
            <div id="loginError"
                 style="margin-top: 15px;
                        color: #f44336;
                        font-size: 12px;
                        font-weight: 600;
                        display: none;
                        padding: 10px;
                        background: rgba(244, 67, 54, 0.1);
                        border-radius: 6px;
                        border-left: 4px solid #f44336;">
                ❌ Usuario o contraseña incorrectos
            </div>
        </div>
    </div>

    <script>
    // HASHES SEGUROS DE LAS CREDENCIALES - EXACTO A COLAB
    const HASH_USUARIO_VALIDO = "{HASH_USUARIO}";
    const HASH_CONTRASENA_VALIDA = "{HASH_CONTRASENA}";

    // Función para calcular hash - EXACTO
    async function calcularHash(texto) {{
        const salt = "ProgramaCordoba25/26-SancorSeguro";
        const encoder = new TextEncoder();
        const data = encoder.encode(texto + salt);
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        return hashHex.substring(0, 16);
    }}

    // Función principal de verificación - EXACTO
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
            const hashUsuarioIngresado = await calcularHash(usuario);
            const hashContrasenaIngresada = await calcularHash(contrasena);

            if (hashUsuarioIngresado === HASH_USUARIO_VALIDO &&
                hashContrasenaIngresada === HASH_CONTRASENA_VALIDA) {{

                document.getElementById("loginScreen").style.opacity = "0";
                setTimeout(function() {{
                    document.getElementById("loginScreen").style.display = "none";
                }}, 500);

                if (document.getElementById("lupitaBuscador")) {{
                    document.getElementById("lupitaBuscador").style.display = "block";
                }}

                if (document.getElementById("btnGraficos")) {{
                    document.getElementById("btnGraficos").style.display = "flex";
                }}

                map.getContainer().style.pointerEvents = "auto";

            }} else {{
                errorDiv.innerHTML = "❌ Usuario o contraseña incorrectos";
                errorDiv.style.display = "block";
                document.getElementById("loginContrasena").value = "";
                document.getElementById("loginContrasena").focus();
            }}
        }} catch (error) {{
            errorDiv.innerHTML = "❌ Error al verificar credenciales";
            errorDiv.style.display = "block";
        }}
    }}

    // Permitir Enter para login - EXACTO
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

    // Al cargar la página - EXACTO
    document.addEventListener("DOMContentLoaded", function() {{
        map.getContainer().style.pointerEvents = "none";

        if (document.getElementById("lupitaBuscador")) {{
            document.getElementById("lupitaBuscador").style.display = "none";
        }}

        if (document.getElementById("btnGraficos")) {{
            document.getElementById("btnGraficos").style.display = "none";
        }}

        setTimeout(() => {{
            document.getElementById("loginUsuario").focus();
        }}, 500);
    }});
    </script>
    '''
    
    agregar_elemento_html_seguro(m, login_html)

    # ========== AJUSTAR VISTA ==========
    if not gdf.empty:
        m.fit_bounds(bounds)

    # ========== GUARDAR ARCHIVO ==========
    m.save(output_file)
    print(f"✅ Aplicación 100% IDÉNTICA A COLAB guardada como: {output_file}")
    
    return output_file

def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("❌ Uso: python generar_app_html_identico.py <ruta_al_geojson> [nombre_salida]")
        print("   Ejemplo: python generar_app_html_identico.py geojson_unificado_actual.geojson app_cordoba_identica.html")
        sys.exit(1)
    
    ruta_geojson = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        output_file = "app_cordoba_identica_colab.html"
    
    if not os.path.exists(ruta_geojson):
        print(f"❌ El archivo {ruta_geojson} no existe")
        sys.exit(1)
    
    try:
        # 1. Cargar datos
        geojson_data, gdf = cargar_geojson(ruta_geojson)
        
        # 2. Encontrar campos
        campos = encontrar_campos(gdf)
        print("\n✅ Campos encontrados:")
        for nombre, campo in campos.items():
            if campo:
                print(f"   • {nombre}: '{campo}'")
        
        # 3. Crear aplicación 100% IDÉNTICA
        crear_app_completa(geojson_data, gdf, campos, output_file)
        
        print(f"\n{'='*80}")
        print("🎉 APLICACIÓN 100% IDÉNTICA A COLAB GENERADA EXITOSAMENTE")
        print(f"{'='*80}")
        print(f"📁 Archivo: {output_file}")
        print(f"📊 Polígonos: {len(gdf)}")
        print(f"🔐 Credenciales: {USUARIO_CORRECTO} / {CONTRASENA_CORRECTA}")
        print(f"\n🌐 Para usar: Abre {output_file} en cualquier navegador")
        print(f"📋 Funcionalidades IDÉNTICAS:")
        print(f"   ✅ Login seguro EXACTO")
        print(f"   ✅ Capa de fotos desde GitHub (200+ líneas JavaScript)")
        print(f"   ✅ Capa de siniestros con fecha y daño")
        print(f"   ✅ Buscador de clientes con botón plegable")
        print(f"   ✅ Dashboard de gráficos idéntico")
        print(f"   ✅ Sistema de leyendas WMS inteligente")
        print(f"   ✅ GPS auto-activado")
        print(f"   ✅ Título, leyenda de cultivos, estilos EXACTOS")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
