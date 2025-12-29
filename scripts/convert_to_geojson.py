#!/usr/bin/env python3
"""
Convierte XLSX/CSV a GeoJSON - Versión para GitHub Actions
"""

import pandas as pd
import json
import geopandas as gpd
from shapely.geometry import shape
import os
from datetime import datetime
import re
import traceback

def repair_truncated_json(json_str):
    """Repara JSON truncado por Excel"""
    if not isinstance(json_str, str):
        return json_str
    
    json_str = json_str.strip()
    
    # Caso 1: Termina con "..."
    if json_str.endswith('...'):
        print("   Detected '...' truncation, attempting repair")
        last_valid = json_str.rfind('"}}')
        if last_valid != -1:
            return json_str[:last_valid + 3]
    
    # Caso 2: No termina correctamente
    elif not (json_str.endswith('}}') or json_str.endswith('}]}') or 
              json_str.endswith('}}}') or json_str.endswith('}]}}')):
        print("   JSON doesn't end properly, attempting repair")
        
        # Buscar patrones de cierre
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
        
        # Buscar último cierre válido
        for end_pattern in ['}}]}', '}}}', '}]}', '}}']:
            pos = json_str.rfind(end_pattern)
            if pos != -1:
                return json_str[:pos + len(end_pattern)]
    
    return json_str

def load_geojson_safe(geojson_data, idx):
    """Carga GeoJSON de forma segura"""
    results = {
        'geodata': None,
        'status': 'ok',
        'message': '',
        'simplified': False
    }
    
    try:
        if isinstance(geojson_data, str):
            try:
                geodata = json.loads(geojson_data)
                results['geodata'] = geodata
                return results
            except json.JSONDecodeError:
                results['status'] = 'repairing'
                results['message'] = 'JSONDecodeError'
                
                # Intentar reparar
                json_repaired = repair_truncated_json(geojson_data)
                
                if json_repaired != geojson_data:
                    try:
                        geodata = json.loads(json_repaired)
                        results['geodata'] = geodata
                        results['status'] = 'repaired'
                        return results
                    except:
                        pass
                
                # Extraer geometría manualmente
                coord_pattern = r'\[-?\d+\.\d+\s*,\s*-?\d+\.\d+\]'
                coords = re.findall(coord_pattern, geojson_data[:10000])
                
                if coords:
                    coords_list = []
                    for coord_str in coords[:20]:
                        try:
                            clean_coord = coord_str.replace(' ', '')
                            lat_lon = json.loads(clean_coord)
                            coords_list.append(lat_lon)
                        except:
                            continue
                    
                    if len(coords_list) >= 3:
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
                        results['geodata'] = geodata
                        results['status'] = 'recovered'
                        results['message'] = f"Geometría recuperada ({len(coords_list)} puntos)"
                        return results
                
                results['status'] = 'error'
                results['message'] = "No se pudo extraer geometría"
                return results
        else:
            results['geodata'] = geojson_data
            return results
            
    except Exception as e:
        results['status'] = 'error'
        results['message'] = f"Error inesperado: {str(e)[:50]}"
        return results

def convert_to_geojson():
    """Función principal de conversión"""
    print("🗺️ Iniciando conversión a GeoJSON")
    
    data_dir = 'data'
    input_files = []
    
    # Buscar archivos de entrada
    for file in ['latest.xlsx', 'latest.csv']:
        filepath = os.path.join(data_dir, file)
        if os.path.exists(filepath):
            input_files.append(filepath)
    
    if not input_files:
        print("❌ No se encontraron archivos de entrada en data/")
        return False
    
    input_file = input_files[0]
    print(f"📖 Leyendo: {input_file}")
    
    try:
        # Leer archivo
        if input_file.endswith('.xlsx'):
            df = pd.read_excel(input_file)
        else:
            df = pd.read_csv(input_file)
        
        print(f"✅ Archivo cargado: {len(df)} filas, {len(df.columns)} columnas")
        
        # Buscar columna GeoJSON
        geojson_col = None
        possible_names = ['GEOJSON', 'geojson', 'GeoJSON', 'GEO JSON', 'geo_json']
        
        for name in possible_names:
            if name in df.columns:
                geojson_col = name
                break
        
        if not geojson_col:
            print("❌ No se encontró columna GeoJSON")
            return False
        
        print(f"✅ Columna GeoJSON: '{geojson_col}'")
        print(f"🔄 Procesando {len(df)} polígonos...")
        
        features = []
        errors = []
        report = []
        
        for idx, row in df.iterrows():
            try:
                geojson_data = row[geojson_col]
                
                if pd.isna(geojson_data):
                    errors.append({
                        'row': idx + 1,
                        'status': 'empty',
                        'message': 'Celda vacía'
                    })
                    continue
                
                # Cargar GeoJSON
                result = load_geojson_safe(geojson_data, idx)
                geodata = result['geodata']
                
                if not geodata:
                    errors.append({
                        'row': idx + 1,
                        'status': result['status'],
                        'message': result['message']
                    })
                    continue
                
                # Extraer geometría
                geometry = None
                properties = {}
                
                if isinstance(geodata, dict) and 'type' in geodata and geodata['type'] == 'FeatureCollection':
                    if 'features' in geodata and len(geodata['features']) > 0:
                        feature = geodata['features'][0]
                        if 'geometry' in feature:
                            geometry = shape(feature['geometry'])
                            if 'properties' in feature:
                                properties = feature['properties']
                
                if geometry is None:
                    errors.append({
                        'row': idx + 1,
                        'status': 'no_geometry',
                        'message': 'No se encontró geometría válida'
                    })
                    continue
                
                # Preparar propiedades
                final_props = {}
                
                # Datos del lote
                try:
                    if 'lot' in properties:
                        lot = properties['lot']
                        final_props.update({
                            'lot_id_json': lot.get('id'),
                            'lot_name_json': lot.get('name'),
                            'crop_json': lot.get('crop', {}).get('name'),
                            'planting_date_json': lot.get('planting_date'),
                            'hectares_declared_json': lot.get('hectares_declared')
                        })
                except:
                    pass
                
                # Agregar todas las columnas del Excel/CSV
                for col in df.columns:
                    if col != geojson_col:
                        valor = row[col]
                        if pd.isna(valor):
                            final_props[col] = None
                        elif isinstance(valor, (pd.Timestamp, datetime)):
                            final_props[col] = valor.strftime('%Y-%m-%d')
                        elif isinstance(valor, (dict, list)):
                            final_props[col] = str(valor)[:100]
                        else:
                            final_props[col] = valor
                
                # Metadatos
                final_props['excel_row_num'] = idx + 1
                final_props['processed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
                final_props['processing_status'] = result['status']
                
                # Crear feature
                feature_gdf = {
                    "type": "Feature",
                    "geometry": geometry.__geo_interface__,
                    "properties": final_props
                }
                
                features.append(feature_gdf)
                report.append({
                    'row': idx + 1,
                    'status': result['status'],
                    'simplified': result.get('simplified', False),
                    'message': result['message']
                })
                
            except Exception as e:
                errors.append({
                    'row': idx + 1,
                    'status': 'critical_error',
                    'message': f"Error crítico: {str(e)[:100]}"
                })
        
        # Crear GeoJSON final
        if features:
            feature_collection = {
                "type": "FeatureCollection",
                "features": features
            }
            
            # Guardar GeoJSON
            output_file = os.path.join(data_dir, 'latest.geojson')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(feature_collection, f, ensure_ascii=False, indent=2)
            
            print(f"✅ GeoJSON creado: {output_file}")
            print(f"📊 Estadísticas:")
            print(f"   • Total filas: {len(df)}")
            print(f"   • Exitosa: {len(features)}")
            print(f"   • Con errores: {len(errors)}")
            
            # Guardar reporte
            if errors:
                report_file = os.path.join(data_dir, 'conversion_report.json')
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'summary': {
                            'total_rows': len(df),
                            'successful': len(features),
                            'errors': len(errors)
                        },
                        'errors': errors[:50],
                        'report': report[:100]
                    }, f, ensure_ascii=False, indent=2)
                print(f"📋 Reporte guardado: {report_file}")
            
            return True
        else:
            print("❌ No se crearon polígonos válidos")
            return False
            
    except Exception as e:
        print(f"❌ Error en conversión: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = convert_to_geojson()
    if success:
        print("🎉 Conversión completada exitosamente")
        exit(0)
    else:
        print("❌ Conversión falló")
        exit(1)
