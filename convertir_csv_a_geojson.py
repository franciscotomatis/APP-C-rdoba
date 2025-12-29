"""
CONVERTIDOR CSV A GEOJSON - Versión para GitHub Actions
Adaptado del script original para funcionar automáticamente
"""
import pandas as pd
import json
import geopandas as gpd
from shapely.geometry import shape
import os
import sys
from datetime import datetime
import re
import traceback

print("=" * 80)
print("🔄 CONVERTIDOR CSV A GEOJSON - PARA GITHUB ACTIONS")
print("=" * 80)

# ============================================
# FUNCIONES AUXILIARES PARA MANEJAR JSON LARGOS
# ============================================

def reparar_json_truncado(json_str):
    """
    Repara un JSON que fue truncado por Excel
    Excel tiene límite de 32,767 caracteres por celda
    """
    if not isinstance(json_str, str):
        return json_str
    
    # Verificar si parece estar truncado
    json_str = json_str.strip()
    
    # Caso 1: Termina con "..."
    if json_str.endswith('...'):
        print("   Detected '...' truncation, attempting repair")
        # Buscar último cierre completo
        last_valid = json_str.rfind('"}}')
        if last_valid != -1:
            return json_str[:last_valid + 3]
    
    # Caso 2: No termina correctamente
    elif not (json_str.endswith('}}') or json_str.endswith('}]}') or 
              json_str.endswith('}}}') or json_str.endswith('}]}}')):
        print("   JSON doesn't end properly, attempting repair")
        
        # Buscar patrones de cierre comunes
        patterns = [
            (r'\}\}\]\}$', 4),  # }}]}
            (r'\}\}\}$', 3),     # }}}
            (r'\}\]\}$', 3),     # }]}
            (r'\}\}$', 2),       # }}
        ]
        
        for pattern, length in patterns:
            match = re.search(pattern, json_str)
            if match:
                return json_str
        
        # Si no encuentra patrón, buscar último cierre válido
        for end_pattern in ['}}]}', '}}}', '}]}', '}}']:
            pos = json_str.rfind(end_pattern)
            if pos != -1:
                return json_str[:pos + len(end_pattern)]
    
    return json_str

def simplificar_geojson_automatico(geodata):
    """
    Simplifica automáticamente GeoJSONs que son demasiado largos
    Mantiene la información esencial
    """
    if not isinstance(geodata, dict) or 'features' not in geodata:
        return geodata
    
    features = geodata['features']
    if not features:
        return geodata
    
    for feature in features:
        props = feature.get('properties', {})
        
        # 1. Si tiene analysis, verificar interfering_zones
        if 'analysis' in props:
            analysis = props['analysis']
            
            # Reducir interfering_zones si son demasiadas
            if 'interfering_zones' in analysis:
                zones = analysis['interfering_zones']
                if len(zones) > 20:
                    print(f"      Simplificando {len(zones)} interfering_zones...")
                    # Mantener las más importantes (con mayor intersection_percentage)
                    try:
                        zones_sorted = sorted(
                            zones,
                            key=lambda x: x.get('properties', {}).get('intersection_percentage', 0),
                            reverse=True
                        )
                        # Mantener máximo 15 zonas
                        analysis['interfering_zones'] = zones_sorted[:15]
                        print(f"      → Reducido a {len(analysis['interfering_zones'])} zonas")
                    except:
                        # Si falla el sorting, mantener las primeras 15
                        analysis['interfering_zones'] = zones[:15]
            
            # 2. Redondear números para reducir longitud
            if 'stats' in analysis and 'zone_stats' in analysis['stats']:
                for stat in analysis['stats']['zone_stats']:
                    for key in ['hectares', 'intersection_area', 'intersection_percentage']:
                        if key in stat and isinstance(stat[key], (int, float)):
                            # Redondear a 2 decimales
                            stat[key] = round(stat[key], 2)
    
    return geodata

def cargar_geojson_seguro(geojson_data, idx):
    """
    Carga GeoJSON de forma segura, reparando si es necesario
    """
    resultados = {
        'geodata': None,
        'estado': 'ok',
        'mensaje': '',
        'simplificado': False
    }
    
    try:
        # Si es string, parsear JSON
        if isinstance(geojson_data, str):
            # Paso 1: Intentar parsear directamente
            try:
                geodata = json.loads(geojson_data)
                resultados['geodata'] = geodata
                return resultados
            except json.JSONDecodeError as e:
                resultados['estado'] = 'reparando'
                resultados['mensaje'] = f"JSONDecodeError: {str(e)[:50]}"
                print(f"   Fila {idx}: JSON inválido, intentando reparar...")
                
                # Paso 2: Reparar JSON truncado
                json_reparado = reparar_json_truncado(geojson_data)
                
                if json_reparado != geojson_data:
                    print(f"   Fila {idx}: JSON reparado, intentando cargar...")
                    try:
                        geodata = json.loads(json_reparado)
                        resultados['geodata'] = geodata
                        resultados['estado'] = 'reparado'
                        return resultados
                    except:
                        pass
                
                # Paso 3: Si sigue fallando, extraer geometría manualmente
                print(f"   Fila {idx}: Extracción manual de geometría...")
                
                # Buscar coordenadas en el texto
                coord_pattern = r'\[-?\d+\.\d+\s*,\s*-?\d+\.\d+\]'
                coords = re.findall(coord_pattern, geojson_data[:10000])
                
                if coords:
                    coords_list = []
                    for coord_str in coords[:20]:  # Limitar a 20 puntos
                        try:
                            # Limpiar y parsear coordenadas
                            clean_coord = coord_str.replace(' ', '')
                            lat_lon = json.loads(clean_coord)
                            coords_list.append(lat_lon)
                        except:
                            continue
                    
                    if len(coords_list) >= 3:
                        # Crear FeatureCollection mínima
                        geodata = {
                            "type": "FeatureCollection",
                            "features": [{
                                "type": "Feature",
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [coords_list + [coords_list[0]]]
                                },
                                "properties": {
                                    "lot": {
                                        "id": idx,
                                        "name": f"Lote Recuperado {idx}",
                                        "hectares_declared": 0
                                    },
                                    "warning": "GEOMETRÍA RECUPERADA - DATOS INCOMPLETOS"
                                }
                            }]
                        }
                        resultados['geodata'] = geodata
                        resultados['estado'] = 'recuperado'
                        resultados['mensaje'] = f"Geometría recuperada ({len(coords_list)} puntos)"
                        return resultados
                
                # Paso 4: Crear geometría vacía
                resultados['estado'] = 'error'
                resultados['mensaje'] = "No se pudo extraer geometría"
                return resultados
        else:
            # Ya es un diccionario
            resultados['geodata'] = geojson_data
            return resultados
            
    except Exception as e:
        resultados['estado'] = 'error'
        resultados['mensaje'] = f"Error inesperado: {str(e)[:50]}"
        return resultados

# ============================================
# FUNCIÓN PRINCIPAL DE PROCESAMIENTO
# ============================================

def procesar_csv_directo():
    """Función principal para procesar CSV directamente"""
    
    archivo_csv = "datos_actualizados.csv"
    
    print(f"📖 Leyendo {archivo_csv}...")
    
    try:
        # Leer CSV en lugar de Excel
        df = pd.read_csv(archivo_csv, encoding='utf-8')
        
        print(f"✅ CSV cargado: {len(df)} filas, {len(df.columns)} columnas")
        print(f"📋 Columnas detectadas:")
        for i, col in enumerate(df.columns.tolist(), 1):
            print(f"   {i:2d}. {col}")
        
        # Buscar columna GeoJSON automáticamente
        columna_geojson = None
        posibles_nombres = ['GEOJSON', 'geojson', 'GeoJSON', 'GEO JSON', 'geo_json']
        
        for nombre in posibles_nombres:
            if nombre in df.columns:
                columna_geojson = nombre
                break
        
        if not columna_geojson:
            print(f"❌ ERROR: No se encontró columna 'GEOJSON'")
            print(f"   Columnas disponibles: {list(df.columns)}")
            return
        
        print(f"\n✅ Columna GeoJSON detectada: '{columna_geojson}'")
        
        # Llamar a la función de procesamiento
        procesar_datos(df, columna_geojson, archivo_csv)
            
    except Exception as e:
        print(f"❌ Error al leer CSV: {str(e)}")
        print(traceback.format_exc())

def procesar_datos(df, columna_geojson, archivo_nombre):
    print(f"\n🔄 Procesando {len(df)} polígonos...")
    print("-" * 80)
    
    features = []
    errores_detallados = []
    reporte_filas = []
    
    for idx, row in df.iterrows():
        try:
            # Obtener datos GeoJSON
            geojson_data = row[columna_geojson]
            
            # Manejar datos faltantes
            if pd.isna(geojson_data):
                errores_detallados.append({
                    'fila': idx + 1,
                    'estado': 'vacio',
                    'mensaje': 'Celda vacía',
                    'geometria': None
                })
                continue
            
            # Cargar GeoJSON de forma segura
            resultado = cargar_geojson_seguro(geojson_data, idx)
            geodata = resultado['geodata']
            
            if not geodata:
                errores_detallados.append({
                    'fila': idx + 1,
                    'estado': resultado['estado'],
                    'mensaje': resultado['mensaje'],
                    'geometria': None
                })
                continue
            
            # Si el JSON fue reparado o recuperado, simplificar si es muy largo
            if resultado['estado'] in ['reparado', 'recuperado']:
                # Verificar si es muy largo (más de 30,000 caracteres al serializar)
                try:
                    json_str = json.dumps(geodata)
                    if len(json_str) > 30000:
                        print(f"   Fila {idx+1}: GeoJSON largo ({len(json_str)} chars), simplificando...")
                        geodata = simplificar_geojson_automatico(geodata)
                        resultado['simplificado'] = True
                except:
                    pass
            
            # EXTRAER GEOMETRÍA
            geometry = None
            propiedades = {}
            
            # CASO 1: FeatureCollection (tu caso)
            if isinstance(geodata, dict) and 'type' in geodata and geodata['type'] == 'FeatureCollection':
                if 'features' in geodata and len(geodata['features']) > 0:
                    feature = geodata['features'][0]
                    if 'geometry' in feature:
                        geometry = shape(feature['geometry'])
                        if 'properties' in feature:
                            propiedades = feature['properties']
            
            if geometry is None:
                errores_detallados.append({
                    'fila': idx + 1,
                    'estado': 'sin_geometria',
                    'mensaje': 'No se encontró geometría válida',
                    'geometria': None
                })
                continue
            
            # PREPARAR PROPIEDADES
            props_final = {}
            
            # 1. Datos del lote (del GeoJSON)
            try:
                if 'lot' in propiedades:
                    lot = propiedades['lot']
                    props_final.update({
                        'lot_id_json': lot.get('id'),
                        'lote_nombre_json': lot.get('name'),
                        'cultivo_json': lot.get('crop', {}).get('name'),
                        'fecha_siembra_json': lot.get('planting_date'),
                        'hectareas_decl_json': lot.get('hectares_declared'),
                        'cultivo_anterior_json': lot.get('crop_season_previous'),
                        'rendimiento_prev_json': lot.get('yield_kg_ha_previous')
                    })
            except Exception as e:
                props_final['error_lot_data'] = f"Error: {str(e)[:50]}"
            
            # 2. Datos de cotización (del GeoJSON)
            try:
                if 'quote_lot' in propiedades:
                    quote = propiedades['quote_lot']
                    props_final.update({
                        'estado_cotizacion': quote.get('status_display'),
                        'suma_asegurada_json': quote.get('sum_insured'),
                        'hectareas_aseg_json': quote.get('hectares_insured'),
                        'porcentaje_aseg_json': quote.get('percentage_insured'),
                        'cz4_zona_json': quote.get('cz4_zone')
                    })
            except Exception as e:
                props_final['error_quote_data'] = f"Error: {str(e)[:50]}"
            
            # 3. AGREGAR TODAS LAS COLUMNAS DEL CSV
            for col in df.columns:
                if col != columna_geojson:
                    valor = row[col]
                    
                    if pd.isna(valor):
                        props_final[col] = None
                    elif isinstance(valor, (pd.Timestamp, datetime)):
                        props_final[col] = valor.strftime('%Y-%m-%d')
                    elif isinstance(valor, (dict, list)):
                        props_final[col] = str(valor)[:100]
                    else:
                        props_final[col] = valor
            
            # 4. Agregar metadatos de procesamiento
            props_final['excel_fila_num'] = idx + 1
            props_final['procesado_en'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            props_final['estado_procesamiento'] = resultado['estado']
            
            if resultado['simplificado']:
                props_final['geojson_simplificado'] = 'SÍ'
            
            # CREAR FEATURE
            feature_gdf = {
                "type": "Feature",
                "geometry": geometry.__geo_interface__,
                "properties": props_final
            }
            
            features.append(feature_gdf)
            
            # Registrar en reporte
            reporte_filas.append({
                'fila': idx + 1,
                'estado': resultado['estado'],
                'simplificado': resultado['simplificado'],
                'mensaje': resultado['mensaje']
            })
            
        except Exception as e:
            error_msg = f"Error crítico: {str(e)[:100]}"
            errores_detallados.append({
                'fila': idx + 1,
                'estado': 'error_critico',
                'mensaje': error_msg,
                'geometria': None
            })
    
    # ============================================
    # 📊 GENERAR REPORTE COMPLETO
    # ============================================
    print(f"\n{'='*80}")
    print("📊 REPORTE DE PROCESAMIENTO")
    print(f"{'='*80}")
    
    total_filas = len(df)
    exitosas = len(features)
    errores = len(errores_detallados)
    
    # Estadísticas por estado
    estados = {}
    for item in reporte_filas:
        estado = item['estado']
        estados[estado] = estados.get(estado, 0) + 1
    
    print(f"\n📈 ESTADÍSTICAS:")
    print(f"   • Total de filas procesadas: {total_filas}")
    print(f"   • ✅ Fila exitosas: {exitosas}")
    print(f"   • ⚠️  Fila con advertencias: {errores - estados.get('error', 0)}")
    print(f"   • ❌ Fila con errores: {estados.get('error', 0)}")
    
    print(f"\n🏷️  DISTRIBUCIÓN POR ESTADO:")
    for estado, count in estados.items():
        porcentaje = (count / total_filas) * 100
        print(f"   • {estado.upper()}: {count} filas ({porcentaje:.1f}%)")
    
    # Mostrar filas simplificadas
    filas_simplificadas = [f for f in reporte_filas if f.get('simplificado')]
    if filas_simplificadas:
        print(f"\n⚠️  FILAS SIMPLIFICADAS (JSON demasiado largo):")
        for fila in filas_simplificadas[:5]:
            print(f"   • Fila {fila['fila']}: {fila['mensaje']}")
        if len(filas_simplificadas) > 5:
            print(f"   • ... y {len(filas_simplificadas) - 5} más")
    
    # Mostrar errores detallados
    if errores_detallados:
        print(f"\n🔍 ERRORES DETALLADOS:")
        for error in errores_detallados[:10]:
            print(f"   • Fila {error['fila']}: [{error['estado']}] {error['mensaje']}")
        if len(errores_detallados) > 10:
            print(f"   • ... y {len(errores_detallados) - 10} más errores")
    
    # ============================================
    # 📁 CREAR ARCHIVOS GIS
    # ============================================
    if features:
        print(f"\n{'='*80}")
        print("🗺️  CREANDO ARCHIVOS GIS...")
        
        try:
            # Crear GeoDataFrame
            feature_collection = {
                "type": "FeatureCollection",
                "features": features
            }
            
            gdf = gpd.GeoDataFrame.from_features(feature_collection)
            gdf.crs = "EPSG:4326"  # WGS84
            
            print(f"✅ GeoDataFrame creado con {len(gdf)} polígonos")
            
            # 📁 GUARDAR ARCHIVOS
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            
            # 1. GeoJSON principal (con nombre fijo para la app)
            geojson_file = "datos_actualizados.geojson"
            gdf.to_file(geojson_file, driver='GeoJSON')
            print(f"   ✅ GeoJSON: {geojson_file}")
            
            # 2. GeoJSON con timestamp (backup)
            geojson_backup = f"poligonos_{timestamp}.geojson"
            gdf.to_file(geojson_backup, driver='GeoJSON')
            print(f"   ✅ Backup: {geojson_backup}")
            
            # 3. Reporte CSV
            reporte_csv = f"reporte_procesamiento_{timestamp}.csv"
            reporte_df = pd.DataFrame(reporte_filas)
            reporte_df.to_csv(reporte_csv, index=False, encoding='utf-8')
            print(f"   📊 Reporte CSV: {reporte_csv}")
            
            # 4. KML (opcional)
            try:
                kml_file = f"poligonos_{timestamp}.kml"
                gdf.to_file(kml_file, driver='KML')
                print(f"   ✅ KML: {kml_file}")
            except:
                print(f"   ⚠️  No se pudo crear KML")
            
            print(f"\n{'='*80}")
            print("📋 RESUMEN FINAL")
            print(f"{'='*80}")
            
            print(f"✅ ¡PROCESO COMPLETADO EXITOSAMENTE!")
            print(f"📁 Archivos creados:")
            print(f"   • {geojson_file} - Para la aplicación web")
            print(f"   • {geojson_backup} - Backup con timestamp")
            print(f"   • {reporte_csv} - Reporte de procesamiento")
            print(f"\n📊 Estadísticas finales:")
            print(f"   • Total polígonos: {len(gdf)}")
            print(f"   • Exitosa: {exitosas}")
            print(f"   • Con errores: {errores}")
            
        except Exception as e:
            print(f"\n❌ Error al crear archivos GIS: {str(e)}")
            print(traceback.format_exc())
            
            # Crear GeoJSON de respaldo mínimo
            print(f"\n💡 Creando archivo de respaldo...")
            geojson_respaldo = f"respaldo_{timestamp}.geojson"
            feature_collection = {
                "type": "FeatureCollection",
                "features": features
            }
            
            with open(geojson_respaldo, 'w', encoding='utf-8') as f:
                json.dump(feature_collection, f, ensure_ascii=False, indent=2)
            
            print(f"   ✅ GeoJSON de respaldo creado: {geojson_respaldo}")
    
    else:
        print(f"\n❌ No se crearon polígonos válidos")
        print(f"   Verifica que la columna '{columna_geojson}' contenga datos GeoJSON válidos")

# ============================================
# EJECUCIÓN PRINCIPAL
# ============================================

if __name__ == "__main__":
    print(f"📅 Inicio del proceso: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar que existe el archivo CSV
    if not os.path.exists("datos_actualizados.csv"):
        print("❌ ERROR: No se encontró el archivo 'datos_actualizados.csv'")
        print("   Ejecuta primero el script de descarga")
        sys.exit(1)
    
    # Ejecutar conversión
    procesar_csv_directo()
    
    print(f"\n✅ Proceso finalizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
