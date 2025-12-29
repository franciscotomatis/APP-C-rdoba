// ============================================
// FUNCIONES ADICIONALES PARA LA APP
// (EXACTAMENTE IGUALES A TU APP ORIGINAL)
// ============================================

// 1. CREAR BUSCADOR DE CLIENTES (LUPA AZUL)
function crearBuscadorClientes(clientesSet) {
    if (!clientesSet || clientesSet.size === 0) {
        console.log('⚠️ No se encontraron clientes para el buscador');
        return;
    }
    
    const clientes = Array.from(clientesSet).sort();
    const buscadorDiv = document.getElementById('buscadorClientes');
    const numPoligonos = geojsonData ? geojsonData.features.length : 0;
    
    let contenido = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="font-weight: bold; color: #000000; font-size: 12px; display: flex; align-items: center;">
                <span style="margin-right: 5px;">🔍</span>
                Buscar cliente
            </div>
            <button id="toggleBuscador" style="background: none; border: none; cursor: pointer; font-size: 14px; color: #000000;">▲</button>
        </div>
        
        <div id="contenidoBuscador">
            <div style="margin-bottom: 8px;">
                <input list="clientesList" id="clienteInput" placeholder="Escribe o selecciona..." 
                       style="width: 100%; padding: 5px; border: 1px solid #ddd; border-radius: 3px; font-size: 11px;">
                <datalist id="clientesList">
                    ${clientes.map(cliente => `<option value="${cliente}">`).join('')}
                </datalist>
            </div>
            
            <div style="display: flex; gap: 5px; margin-bottom: 6px;">
                <button onclick="filtrarCliente()" style="flex: 1; background-color: #4CAF50; color: white; border: none; padding: 5px; border-radius: 3px; cursor: pointer; font-size: 10px;">
                    Filtrar
                </button>
                <button onclick="resetearFiltro()" style="flex: 1; background-color: #f44336; color: white; border: none; padding: 5px; border-radius: 3px; cursor: pointer; font-size: 10px;">
                    Reset
                </button>
            </div>
            
            <div id="estadoFiltro" style="font-size: 9px; color: #666; margin-top: 6px; padding-top: 5px; border-top: 1px solid #000000;">
                Mostrando todos (${numPoligonos})
            </div>
        </div>
    `;
    
    buscadorDiv.innerHTML = contenido;
    
    // Configurar toggle
    let contenidoVisible = true;
    const toggleBtn = document.getElementById('toggleBuscador');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            const contenido = document.getElementById('contenidoBuscador');
            const lupita = document.getElementById('buscadorClientes');
            
            if (contenidoVisible) {
                contenido.style.display = 'none';
                this.innerHTML = '▼';
                lupita.style.width = '150px';
                lupita.style.padding = '5px 8px';
            } else {
                contenido.style.display = 'block';
                this.innerHTML = '▲';
                lupita.style.width = '240px';
                lupita.style.padding = '10px 12px';
            }
            contenidoVisible = !contenidoVisible;
        });
    }
    
    // Permitir Enter para filtrar
    const inputCliente = document.getElementById('clienteInput');
    if (inputCliente) {
        inputCliente.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                filtrarCliente();
            }
        });
    }
}

// 2. FUNCIONES DE FILTRADO (IGUAL A TU APP)
function filtrarCliente() {
    const input = document.getElementById('clienteInput');
    if (!input) return;
    
    const valor = input.value.toLowerCase();
    if (!valor) {
        alert('Por favor, escribe o selecciona un cliente');
        return;
    }
    
    let boundsFiltrados = null;
    let contador = 0;
    
    // Almacenar estilos originales si no están guardados
    geoLayer.eachLayer(function(layer) {
        if (!layer._estiloOriginal) {
            layer._estiloOriginal = {
                fillColor: layer.options.fillColor,
                color: layer.options.color,
                weight: layer.options.weight,
                fillOpacity: layer.options.fillOpacity,
                opacity: layer.options.opacity,
                interactive: layer.options.interactive
            };
        }
    });
    
    // Filtrar
    geoLayer.eachLayer(function(layer) {
        const propiedades = layer.feature.properties;
        const clienteEnPoligono = propiedades[campoCliente];
        
        if (clienteEnPoligono && clienteEnPoligono.toString().toLowerCase().includes(valor)) {
            // MOSTRAR
            layer.setStyle({
                fillOpacity: 0.6,
                weight: 2,
                opacity: 1,
                fillColor: layer._estiloOriginal.fillColor,
                color: layer._estiloOriginal.color
            });
            layer.options.interactive = true;
            
            // Agregar a bounds
            const layerBounds = layer.getBounds();
            if (layerBounds) {
                boundsFiltrados = boundsFiltrados ? boundsFiltrados.extend(layerBounds) : layerBounds;
            }
            contador++;
        } else {
            // OCULTAR COMPLETAMENTE
            layer.setStyle({
                fillOpacity: 0,
                weight: 0,
                opacity: 0
            });
            layer.options.interactive = false;
        }
    });
    
    // Actualizar estado
    const estadoDiv = document.getElementById('estadoFiltro');
    if (estadoDiv) {
        if (contador > 0) {
            estadoDiv.innerHTML = `Mostrando ${contador} polígonos`;
            estadoDiv.style.color = '#4CAF50';
            
            // Zoom a los filtrados
            if (boundsFiltrados) {
                map.fitBounds(boundsFiltrados, { padding: [50, 50] });
            }
        } else {
            estadoDiv.innerHTML = '❌ No se encontraron';
            estadoDiv.style.color = '#f44336';
        }
    }
}

function resetearFiltro() {
    const input = document.getElementById('clienteInput');
    if (input) input.value = '';
    
    // Restaurar TODOS los polígonos
    geoLayer.eachLayer(function(layer) {
        if (layer._estiloOriginal) {
            layer.setStyle(layer._estiloOriginal);
            layer.options.interactive = true;
        }
    });
    
    // Restaurar zoom original
    if (boundsGeneral && boundsGeneral.isValid()) {
        map.fitBounds(boundsGeneral);
    }
    
    // Actualizar estado
    const estadoDiv = document.getElementById('estadoFiltro');
    if (estadoDiv) {
        estadoDiv.innerHTML = `Mostrando todos (${geojsonData.features.length})`;
        estadoDiv.style.color = '#666';
    }
}

// 3. CREAR LEYENDA DE CULTIVOS (IGUAL A TU APP)
function crearLeyendaCultivos(superficiePorCultivo, totalSuperficie) {
    if (!superficiePorCultivo || Object.keys(superficiePorCultivo).length === 0) {
        return;
    }
    
    const leyendaDiv = document.getElementById('leyendaCultivos');
    let contenido = `
        <div style="font-weight: bold; color: #2E7D32; margin-bottom: 8px; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
            Cultivos (${Object.keys(superficiePorCultivo).length})
        </div>
    `;
    
    // Ordenar por superficie (mayor a menor) y tomar top 8
    const cultivosOrdenados = Object.entries(superficiePorCultivo)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8);
    
    cultivosOrdenados.forEach(([cultivo, hectareas]) => {
        const porcentaje = totalSuperficie > 0 ? (hectareas / totalSuperficie * 100) : 0;
        const color = obtenerColorPorCultivo(cultivo);
        const nombreCorto = cultivo.length > 15 ? cultivo.substring(0, 15) + '...' : cultivo;
        
        contenido += `
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div class="color-box" style="background-color: ${color};"></div>
                <div style="flex: 1; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 10px; font-weight: bold;">${nombreCorto}</span>
                    <span style="font-size: 9px; color: #666;">${hectareas.toFixed(0)}ha (${porcentaje.toFixed(0)}%)</span>
                </div>
            </div>
        `;
    });
    
    contenido += `
        <div style="margin-top: 6px; padding-top: 4px; border-top: 1px solid #4CAF50; font-size: 10px; font-weight: bold; color: #2E7D32; text-align: center;">
            TOTAL: ${totalSuperficie.toFixed(0)} ha
        </div>
    `;
    
    leyendaDiv.innerHTML = contenido;
}

// 4. CREAR LEYENDA DE PRECIPITACIÓN
function crearLeyendaPrecipitacion() {
    const leyendaDiv = document.getElementById('leyendaPrecip');
    
    leyendaDiv.innerHTML = `
        <div style="font-weight: bold; color: #1E88E5; margin-bottom: 10px; border-bottom: 2px solid #1E88E5; padding-bottom: 6px; font-size: 10px;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span>🌧️</span>
                    <span>Precipitación (mm)</span>
                </div>
                <button onclick="ocultarLeyendaPrecip()" style="background: none; border: none; color: #1E88E5; font-size: 16px; cursor: pointer; padding: 0; line-height: 1;">×</button>
            </div>
        </div>
        
        <div style="margin-bottom: 10px;">
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div style="width: 18px; height: 18px; background-color: #9e9eFF; margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 10px;">0</span>
                    <span style="font-size: 10px; color: #666;">mm</span>
                    <span style="font-size: 10px;">2</span>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div style="width: 18px; height: 18px; background-color: #0000FF; margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 10px;">2</span>
                    <span style="font-size: 10px; color: #666;">mm</span>
                    <span style="font-size: 10px;">5</span>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div style="width: 18px; height: 18px; background-color: #00FFFF; margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 10px;">5</span>
                    <span style="font-size: 10px; color: #666;">mm</span>
                    <span style="font-size: 10px;">10</span>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div style="width: 18px; height: 18px; background-color: #00FF80; margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 10px;">10</span>
                    <span style="font-size: 10px; color: #666;">mm</span>
                    <span style="font-size: 10px;">15</span>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div style="width: 18px; height: 18px; background-color: #00FF00; margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 10px;">15</span>
                    <span style="font-size: 10px; color: #666;">mm</span>
                    <span style="font-size: 10px;">20</span>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div style="width: 18px; height: 18px; background-color: #FFFF00; margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 10px;">20</span>
                    <span style="font-size: 10px; color: #666;">mm</span>
                    <span style="font-size: 10px;">30</span>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div style="width: 18px; height: 18px; background-color: #FFA500; margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 10px;">30</span>
                    <span style="font-size: 10px; color: #666;">mm</span>
                    <span style="font-size: 10px;">50</span>
                </div>
            </div>
            
            <div style="display: flex; align-items: center; margin-bottom: 4px;">
                <div style="width: 18px; height: 18px; background-color: #FF4500; margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 10px;">50</span>
                    <span style="font-size: 10px; color: #666;">mm</span>
                    <span style="font-size: 10px;">100</span>
                </div>
            </div>
            
            <div style="display: flex; align-items: center;">
                <div style="width: 18px; height: 18px; background-color: #FF0000; margin-right: 10px; border: 1px solid #666; border-radius: 3px;"></div>
                <div style="flex: 1; display: flex; justify-content: space-between;">
                    <span style="font-size: 10px; font-weight: bold;">> 100</span>
                    <span style="font-size: 10px; color: #666;">mm</span>
                    <span style="font-size: 10px; font-weight: bold;"></span>
                </div>
            </div>
        </div>
    `;
}

function ocultarLeyendaPrecip() {
    document.getElementById('leyendaPrecip').style.display = 'none';
}

// 5. CREAR PANEL DE GRÁFICOS (COMPARACIÓN ZONAS)
function crearPanelGraficos(hectareasPorZona) {
    const panelDiv = document.getElementById('panelGraficos');
    const zonasOrdenadas = ["1", "2", "3", "4"];
    
    let datosProyectados = [];
    let datosReales = [];
    let diferencias = [];
    let porcentajesDif = [];
    
    // Preparar datos
    zonasOrdenadas.forEach(zona => {
        const proyectado = HECTAREAS_PROYECTADAS[zona] || 0;
        const real = hectareasPorZona[zona] || 0;
        const diferencia = real - proyectado;
        const porcentaje = proyectado > 0 ? (diferencia / proyectado * 100) : 0;
        
        datosProyectados.push(proyectado);
        datosReales.push(real);
        diferencias.push(diferencia);
        porcentajesDif.push(porcentaje);
    });
    
    const maxValor = Math.max(...datosProyectados, ...datosReales) || 100000;
    const totalProyectado = datosProyectados.reduce((a, b) => a + b, 0);
    const totalReal = datosReales.reduce((a, b) => a + b, 0);
    const totalDiferencia = totalReal - totalProyectado;
    const totalPorcentaje = totalProyectado > 0 ? (totalDiferencia / totalProyectado * 100) : 0;
    
    // Generar HTML para gráficos
    let barrasHTML = '';
    let tablaHTML = '';
    
    zonasOrdenadas.forEach((zona, i) => {
        const proyectado = datosProyectados[i];
        const real = datosReales[i];
        const diferencia = diferencias[i];
        const porcentaje = porcentajesDif[i];
        
        const anchoProyectado = Math.min(95, (proyectado / maxValor * 95));
        const anchoReal = Math.min(95, (real / maxValor * 95));
        const colorReal = diferencia >= 0 ? '#2196F3' : '#f44336';
        const colorDiferencia = diferencia >= 0 ? '#4CAF50' : '#f44336';
        const iconoDiferencia = diferencia >= 0 ? '↗️' : '↘️';
        
        // Gráfico de barras
        barrasHTML += `
            <div style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                    <div style="font-weight: bold; color: #333; font-size: 14px;">ZONA ${zona}</div>
                    <div style="font-size: 13px; color: #666;">
                        Diferencia: <span style="font-weight: bold; color: ${colorDiferencia}">
                            ${diferencia.toLocaleString('es-AR', { maximumFractionDigits: 0 })} ha (${porcentaje.toFixed(1)}%) ${iconoDiferencia}
                        </span>
                    </div>
                </div>
                
                <div style="margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                        <span style="font-size: 12px; color: #666;">Proyectado</span>
                        <span style="font-size: 12px; font-weight: bold; color: #2E7D32">${proyectado.toLocaleString('es-AR', { maximumFractionDigits: 0 })} ha</span>
                    </div>
                    <div style="width: 100%; background-color: #f0f0f0; border-radius: 4px; height: 24px; overflow: hidden;">
                        <div style="width: ${anchoProyectado}%; height: 100%; background-color: #2E7D32; border-radius: 4px; display: flex; align-items: center; padding-left: 10px;">
                            <span style="color: white; font-size: 11px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">PROYECTADO</span>
                        </div>
                    </div>
                </div>
                
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 3px;">
                        <span style="font-size: 12px; color: #666;">Actual</span>
                        <span style="font-size: 12px; font-weight: bold; color: ${colorReal}">${real.toLocaleString('es-AR', { maximumFractionDigits: 0 })} ha</span>
                    </div>
                    <div style="width: 100%; background-color: #f0f0f0; border-radius: 4px; height: 24px; overflow: hidden;">
                        <div style="width: ${anchoReal}%; height: 100%; background-color: ${colorReal}; border-radius: 4px; display: flex; align-items: center; padding-left: 10px;">
                            <span style="color: white; font-size: 11px; font-weight: bold; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">ACTUAL</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Tabla
        tablaHTML += `
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 10px; font-weight: bold;">Zona ${zona}</td>
                <td style="padding: 10px; text-align: right;">${proyectado.toLocaleString('es-AR', { maximumFractionDigits: 0 })}</td>
                <td style="padding: 10px; text-align: right; font-weight: bold;">${real.toLocaleString('es-AR', { maximumFractionDigits: 0 })}</td>
                <td style="padding: 10px; text-align: right; color: ${colorDiferencia}; font-weight: bold;">
                    ${diferencia > 0 ? '+' : ''}${diferencia.toLocaleString('es-AR', { maximumFractionDigits: 0 })}
                </td>
                <td style="padding: 10px; text-align: right; color: ${colorDiferencia};">
                    ${porcentaje > 0 ? '+' : ''}${porcentaje.toFixed(1)}%
                </td>
            </tr>
        `;
    });
    
    // HTML completo del panel
    panelDiv.innerHTML = `
        <div style="position: sticky; top: 0; background-color: #2E7D32; color: white; padding: 15px 20px; border-top-left-radius: 15px; border-top-right-radius: 15px; display: flex; justify-content: space-between; align-items: center; z-index: 1;">
            <div style="font-size: 18px; font-weight: bold; display: flex; align-items: center; gap: 10px;">
                <span>📊</span>
                COMPARACIÓN POR ZONA - PROYECTADO vs ACTUAL
            </div>
            <button onclick="togglePanelGraficos()" style="background: none; border: none; color: white; font-size: 24px; cursor: pointer; padding: 0; width: 30px; height: 30px;">×</button>
        </div>
        
        <div style="padding: 20px; max-width: 1000px; margin: 0 auto;">
            <!-- RESUMEN -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px;">
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #2E7D32;">
                    <div style="font-size: 12px; color: #666; margin-bottom: 5px;">TOTAL PROYECTADO</div>
                    <div style="font-size: 22px; font-weight: bold; color: #2E7D32;">${totalProyectado.toLocaleString('es-AR', { maximumFractionDigits: 0 })} ha</div>
                </div>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #2196F3;">
                    <div style="font-size: 12px; color: #666; margin-bottom: 5px;">TOTAL ACTUAL</div>
                    <div style="font-size: 22px; font-weight: bold; color: #2196F3;">${totalReal.toLocaleString('es-AR', { maximumFractionDigits: 0 })} ha</div>
                </div>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #FF9800;">
                    <div style="font-size: 12px; color: #666; margin-bottom: 5px;">DIFERENCIA TOTAL</div>
                    <div style="font-size: 22px; font-weight: bold; color: ${totalDiferencia >= 0 ? '#4CAF50' : '#f44336'};">${totalDiferencia > 0 ? '+' : ''}${totalDiferencia.toLocaleString('es-AR', { maximumFractionDigits: 0 })} ha</div>
                </div>
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #9C27B0;">
                    <div style="font-size: 12px; color: #666; margin-bottom: 5px;">% DE CUMPLIMIENTO</div>
                    <div style="font-size: 22px; font-weight: bold; color: ${totalPorcentaje >= 0 ? '#4CAF50' : '#f44336'};">${totalPorcentaje.toFixed(1)}%</div>
                </div>
            </div>
            
            <!-- GRÁFICO DE BARRAS -->
            <div style="background-color: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <h3 style="margin-top: 0; margin-bottom: 20px; color: #333; font-size: 16px; border-bottom: 2px solid #2E7D32; padding-bottom: 8px;">HECTÁREAS POR ZONA - COMPARACIÓN</h3>
                <div style="display: flex; flex-direction: column; gap: 20px;">${barrasHTML}</div>
            </div>
            
            <!-- TABLA RESUMEN -->
            <div style="background-color: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <h3 style="margin-top: 0; margin-bottom: 15px; color: #333; font-size: 16px;">RESUMEN</h3>
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
                        <tbody>${tablaHTML}</tbody>
                        <tfoot style="background-color: #f9f9f9; font-weight: bold;">
                            <tr>
                                <td style="padding: 10px; border-top: 2px solid #2E7D32;">TOTAL</td>
                                <td style="padding: 10px; text-align: right; border-top: 2px solid #2E7D32;">${totalProyectado.toLocaleString('es-AR', { maximumFractionDigits: 0 })}</td>
                                <td style="padding: 10px; text-align: right; border-top: 2px solid #2E7D32;">${totalReal.toLocaleString('es-AR', { maximumFractionDigits: 0 })}</td>
                                <td style="padding: 10px; text-align: right; border-top: 2px solid #2E7D32; color: ${totalDiferencia >= 0 ? '#4CAF50' : '#f44336'};">${totalDiferencia > 0 ? '+' : ''}${totalDiferencia.toLocaleString('es-AR', { maximumFractionDigits: 0 })}</td>
                                <td style="padding: 10px; text-align: right; border-top: 2px solid #2E7D32; color: ${totalPorcentaje >= 0 ? '#4CAF50' : '#f44336'};">${totalPorcentaje > 0 ? '+' : ''}${totalPorcentaje.toFixed(1)}%</td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>
            
            <!-- INFORMACIÓN -->
            <div style="font-size: 12px; color: #666; padding: 15px; background-color: #f8f9fa; border-radius: 6px; border-left: 4px solid #FF9800;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                    <span>💡</span>
                    <strong>Información para el análisis:</strong>
                </div>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>Datos proyectados: valores estimados para la campaña 25/26</li>
                    <li>Datos actuales: calculados automáticamente del archivo GeoJSON cargado</li>
                    <li>Verde (↑): la zona supera la proyección</li>
                    <li>Rojo (↓): la zona está por debajo de la proyección</li>
                </ul>
            </div>
        </div>
    `;
}

// 6. FUNCIÓN AUXILIAR: OBTENER COLOR POR CULTIVO
function obtenerColorPorCultivo(cultivo) {
    if (!cultivo) return '#9C27B0';
    
    const cultivoLower = String(cultivo).toLowerCase();
    
    if (cultivoLower.includes('soja') || cultivoLower.includes('soya')) {
        return '#4CAF50';
    } else if (cultivoLower.includes('maíz') || cultivoLower.includes('maiz') || cultivoLower.includes('corn')) {
        return '#FFC107';
    } else if (cultivoLower.includes('trigo') || cultivoLower.includes('wheat')) {
        return '#795548';
    } else if (cultivoLower.includes('girasol') || cultivoLower.includes('sunflower')) {
        return '#FF9800';
    } else if (cultivoLower.includes('algodón') || cultivoLower.includes('algodon') || cultivoLower.includes('cotton')) {
        return '#2196F3';
    } else if (cultivoLower.includes('sorgo') || cultivoLower.includes('sorghum')) {
        return '#E91E63';
    } else {
        return '#9C27B0';
    }
}

// 7. EXPORTAR FUNCIONES AL SCOPE GLOBAL
// (Esto es necesario para que funcionen los onclick en los botones)
if (typeof window !== 'undefined') {
    window.filtrarCliente = filtrarCliente;
    window.resetearFiltro = resetearFiltro;
    window.ocultarLeyendaPrecip = ocultarLeyendaPrecip;
    window.togglePanelGraficos = togglePanelGraficos;
}
