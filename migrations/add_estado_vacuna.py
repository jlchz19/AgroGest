#!/usr/bin/env python3
"""
Migration script to add 'estado' field to Vacuna model
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add estado column to vacuna table and update existing records"""
    
    db_path = 'finca_ganadera.db'
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if estado column already exists
        cursor.execute("PRAGMA table_info(vacuna)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'estado' not in columns:
            print("Adding 'estado' column to vacuna table...")
            
            # Add the estado column
            cursor.execute("""
                ALTER TABLE vacuna 
                ADD COLUMN estado TEXT NOT NULL DEFAULT 'pendiente'
            """)
            
            # Update existing records based on fecha_proxima
            cursor.execute("""
                UPDATE vacuna 
                SET estado = CASE 
                    WHEN date(fecha_proxima) < date('now') THEN 'vencida'
                    WHEN date(fecha_proxima) >= date('now') THEN 'aplicada'
                    ELSE 'pendiente'
                END
            """)
            
            conn.commit()
            print("Migration completed successfully!")
            
            # Show summary
            cursor.execute("SELECT estado, COUNT(*) FROM vacuna GROUP BY estado")
            summary = cursor.fetchall()
            print("\nVaccine status summary:")
            for status, count in summary:
                print(f"  {status}: {count}")
                
        else:
            print("Estado column already exists in vacuna table")
            
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
