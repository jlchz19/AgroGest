// Mapa global
let map;
let drawnItems = new L.FeatureGroup();
let drawControl;
let isMapInitialized = false;

// Inicializar el mapa
function initMap() {
    if (isMapInitialized) return;
    
    // Crear el mapa centrado en Colombia
    map = L.map('map', {
        center: [4.5709, -74.2973],
        zoom: 6,
        zoomControl: false, // Desactivar el control de zoom por defecto
        preferCanvas: true,
        tap: false, // Mejora el comportamiento táctil en móviles
        zoomSnap: 0.1,
        zoomDelta: 0.5
    });
    
    // Añadir capa de OpenStreetMap con mejor rendimiento
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        maxZoom: 19,
        detectRetina: true,
        updateWhenIdle: true,
        reuseTiles: true
    }).addTo(map);
    
    // Añadir controles personalizados
    L.control.zoom({
        position: 'topright'
    }).addTo(map);
    
    // Añadir capa para dibujar
    map.addLayer(drawnItems);
    
    // Configurar controles de dibujo
    drawControl = new L.Control.Draw({
        draw: {
            polygon: {
                allowIntersection: false,
                showArea: true,
                metric: true,
                shapeOptions: {
                    color: '#3388ff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.3
                }
            },
            polyline: false,
            rectangle: false,
            circle: false,
            marker: false,
            circlemarker: false
        },
        edit: {
            featureGroup: drawnItems,
            remove: true
        }
    });
    
    map.addControl(drawControl);
    
    // Manejar eventos de dibujo
    map.on(L.Draw.Event.CREATED, function (e) {
        const layer = e.layer;
        drawnItems.clearLayers();
        drawnItems.addLayer(layer);
        document.getElementById('btnGuardarUbicacion').style.display = 'block';
        
        // Actualizar coordenadas en el formulario
        const coords = layer.getLatLngs()[0].map(latlng => [latlng.lat, latlng.lng]);
        document.getElementById('poligono_geojson').value = JSON.stringify({
            type: 'Polygon',
            coordinates: [coords]
        });
    });
    
    map.on(L.Draw.Event.DELETED, function() {
        document.getElementById('poligono_geojson').value = '';
        document.getElementById('btnGuardarUbicacion').style.display = 'none';
    });
    
    isMapInitialized = true;
}

// Cargar polígono existente si existe
function cargarPoligonoExistente(geojsonStr) {
    if (!geojsonStr) return;
    
    try {
        const geojson = JSON.parse(geojsonStr);
        if (geojson && geojson.type === 'Polygon' && geojson.coordinates) {
            const polygon = L.polygon(geojson.coordinates[0].map(coord => [coord[1], coord[0]]), {
                color: '#3388ff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.3
            });
            
            drawnItems.addLayer(polygon);
            map.fitBounds(polygon.getBounds());
            document.getElementById('btnGuardarUbicacion').style.display = 'block';
        }
    } catch (e) {
        console.error('Error al cargar el polígono:', e);
    }
}

// Capturar la ubicación actual del usuario
function obtenerUbicacionActual() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            // Actualizar campos ocultos
            document.getElementById('latitud').value = lat;
            document.getElementById('longitud').value = lng;
            
            // Centrar el mapa en la ubicación actual
            if (map) {
                map.setView([lat, lng], 15);
            }
        }, function(error) {
            console.error('Error al obtener la ubicación:', error);
            alert('No se pudo obtener la ubicación actual. Asegúrate de haber permitido el acceso a la ubicación.');
        });
    } else {
        alert('Tu navegador no soporta geolocalización.');
    }
}

// Capturar la vista del mapa como imagen
function capturarMapa() {
    if (!map) return;
    
    // Obtener el centro del mapa
    const center = map.getCenter();
    const lat = center.lat;
    const lng = center.lng;
    
    // Obtener el polígono si existe
    let polygon = null;
    if (drawnItems.getLayers().length > 0) {
        const layer = drawnItems.getLayers()[0];
        polygon = JSON.stringify({
            type: 'Polygon',
            coordinates: [layer.getLatLngs()[0].map(latlng => [latlng.lng, latlng.lat])]
        });
    }
    
    // Generar una dirección basada en las coordenadas
    const direccion = `Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}`;
    
    // Actualizar los campos del formulario usando la función global
    if (typeof window.actualizarUbicacionDesdeMapa === 'function') {
        window.actualizarUbicacionDesdeMapa(lat, lng, direccion, polygon);
    }
    
    // Obtener el contenedor del mapa
    const mapContainer = document.getElementById('map');
    
    // Usar html2canvas para capturar el mapa
    html2canvas(mapContainer, {
        useCORS: true,
        allowTaint: true,
        scale: 1,
        logging: false,
        onclone: function(clonedDoc) {
            // Asegurarse de que el mapa esté visible en el clon
            const clonedMap = clonedDoc.getElementById('map');
            if (clonedMap) {
                clonedMap.style.visibility = 'visible';
                clonedMap.style.opacity = '1';
            }
        }
    }).then(canvas => {
        // Convertir el canvas a una imagen en base64
        const imageData = canvas.toDataURL('image/png');
        
        // Actualizar el campo oculto con la imagen
        document.getElementById('imagen_mapa_base64').value = imageData;
        
        // Mostrar vista previa
        const previewContainer = document.getElementById('mapaPreviewContainer');
        const previewImg = document.getElementById('mapaPreview');
        
        if (previewContainer && previewImg) {
            previewImg.src = imageData;
            previewContainer.style.display = 'block';
        }
        
        // Cerrar el modal después de guardar
        const modal = bootstrap.Modal.getInstance(document.getElementById('mapModal'));
        if (modal) {
            modal.hide();
        }
        
        // Mostrar mensaje de éxito
        alert('Ubicación guardada correctamente');
    }).catch(error => {
        console.error('Error al capturar el mapa:', error);
        alert('Error al guardar la ubicación. Por favor, inténtalo de nuevo.');
    });
}

// Inicializar el mapa cuando se muestre el modal
document.addEventListener('DOMContentLoaded', function() {
    const mapModal = document.getElementById('mapModal');
    let mapInitialized = false;
    let resizeObserver;
    
    // Función para inicializar el mapa
    function initializeMap() {
        if (!mapInitialized) {
            initMap();
            mapInitialized = true;
            
            // Configurar el evento de redimensionamiento para el mapa
            map.whenReady(function() {
                // Pequeño retraso para asegurar que el contenedor tenga dimensiones
                setTimeout(function() {
                    map.invalidateSize({ animate: false });
                    map.setView([4.5709, -74.2973], 6);
                    
                    // Configurar el observador de cambios de tamaño
                    const mapContainer = document.getElementById('map');
                    if (mapContainer && 'ResizeObserver' in window) {
                        if (resizeObserver) resizeObserver.disconnect();
                        
                        resizeObserver = new ResizeObserver(function() {
                            if (map) {
                                map.invalidateSize({ animate: false });
                            }
                        });
                        
                        resizeObserver.observe(mapContainer);
                    }
                }, 50);
            });
        } else {
            // Forzar el redibujado del mapa cuando se muestra el modal
            setTimeout(function() {
                if (!map) return;
                
                map.invalidateSize({ animate: false, pan: false });
                
                // Centrar el mapa si ya hay un polígono dibujado
                if (drawnItems && drawnItems.getLayers().length > 0) {
                    map.fitBounds(drawnItems.getBounds(), { 
                        padding: [30, 30],
                        maxZoom: 15
                    });
                } else {
                    map.setView([4.5709, -74.2973], 6, { animate: false });
                }
            }, 100);
        }
    }
    
    // Inicializar el mapa cuando se muestra el modal
    if (mapModal) {
        mapModal.addEventListener('shown.bs.modal', function() {
            initializeMap();
            
            // Asegurarse de que el mapa se redimensione después de las animaciones
            setTimeout(function() {
                if (map) map.invalidateSize({ animate: false });
            }, 300);
        });
        
        // Limpiar el observador cuando se cierra el modal
        mapModal.addEventListener('hidden.bs.modal', function() {
            if (resizeObserver) {
                resizeObserver.disconnect();
            }
        });
    }
    
    // Manejar el evento de redimensionamiento de la ventana
    let resizeTimer;
    const handleResize = function() {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function() {
            if (map) {
                map.invalidateSize({ 
                    animate: false,
                    pan: false,
                    debounceMoveend: true
                });
            }
        }, 100);
    };
    
    window.addEventListener('resize', handleResize);
    
    // Limpiar el event listener cuando se desmonte el componente
    document.addEventListener('turbolinks:before-render', function() {
        window.removeEventListener('resize', handleResize);
        if (resizeObserver) {
            resizeObserver.disconnect();
        }
    });

    // Botón de ubicación actual
    const btnUbicacionActual = document.getElementById('btnUbicacionActual');
    if (btnUbicacionActual) {
        btnUbicacionActual.addEventListener('click', obtenerUbicacionActual);
    }

    // Botón de guardar ubicación
    const btnGuardarUbicacion = document.getElementById('btnGuardarUbicacion');
    if (btnGuardarUbicacion) {
        btnGuardarUbicacion.addEventListener('click', capturarMapa);
    }
});
