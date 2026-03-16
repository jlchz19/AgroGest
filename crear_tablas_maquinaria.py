#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migración para agregar tablas de maquinaria a la base de datos
"""

import sqlite3
import os
from datetime import datetime

def agregar_tablas_maquinaria():
    """Agrega las tablas de maquinaria a la base de datos existente"""
    
    # Ruta de la base de datos
    db_path = os.path.join(os.path.dirname(__file__), 'finca_ganadera.db')
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Crear tabla maquinaria
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maquinaria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                finca_id INTEGER NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                tipo VARCHAR(50) NOT NULL,
                marca VARCHAR(50),
                modelo VARCHAR(50),
                numero_serie VARCHAR(100),
                año_fabricacion INTEGER,
                fecha_adquisicion DATE,
                valor_compra FLOAT,
                estado VARCHAR(20) DEFAULT 'operativo',
                ubicacion_actual VARCHAR(100),
                horas_uso FLOAT DEFAULT 0,
                ultimo_mantenimiento DATE,
                proximo_mantenimiento DATE,
                responsable VARCHAR(100),
                observaciones TEXT,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (finca_id) REFERENCES finca (id)
            )
        ''')
        
        # Crear tabla mantenimiento_maquinaria
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mantenimiento_maquinaria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                maquinaria_id INTEGER NOT NULL,
                tipo_mantenimiento VARCHAR(50) NOT NULL,
                descripcion TEXT NOT NULL,
                fecha_mantenimiento DATE NOT NULL,
                costo FLOAT,
                tecnico VARCHAR(100),
                piezas_cambiadas TEXT,
                proximo_mantenimiento DATE,
                responsable_registro VARCHAR(100),
                observaciones TEXT,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (maquinaria_id) REFERENCES maquinaria (id)
            )
        ''')
        
        # Confirmar cambios
        conn.commit()
        print("✅ Tablas de maquinaria creadas exitosamente")
        
        # Verificar que las tablas existen
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('maquinaria', 'mantenimiento_maquinaria')")
        tablas = cursor.fetchall()
        
        print(f"📋 Tablas verificadas: {[tabla[0] for tabla in tablas]}")
        
        # Cerrar conexión
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear las tablas de maquinaria: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando migración de tablas de maquinaria...")
    print("=" * 50)
    
    if agregar_tablas_maquinaria():
        print("=" * 50)
        print("✅ Migración completada exitosamente")
        print("🎉 Las tablas de maquinaria están listas para usar")
    else:
        print("=" * 50)
        print("❌ La migración falló")
        print("🔧 Por favor, revise los errores mostrados arriba")
