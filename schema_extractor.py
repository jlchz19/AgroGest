import sqlite3
import sys

def get_schema():
    conn = sqlite3.connect('finca_ganadera.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("-- Base de datos finca_ganadera - Script SQL compatible con MySQL")
    print("-- Generado desde SQLite")
    print()
    
    for table in tables:
        table_name = table[0]
        print(f"-- Tabla: {table_name}")
        print(f"CREATE TABLE {table_name} (")
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        for i, col in enumerate(columns):
            col_name = col[1]
            col_type = col[2]
            not_null = col[3]
            default_val = col[4]
            pk = col[5]
            
            # Convert SQLite types to MySQL
            if col_type.upper() == 'INTEGER':
                mysql_type = 'INT'
            elif col_type.upper() == 'TEXT':
                mysql_type = 'TEXT'
            elif col_type.upper().startswith('VARCHAR'):
                mysql_type = col_type.upper()
            elif col_type.upper() == 'REAL':
                mysql_type = 'DOUBLE'
            elif col_type.upper() == 'BLOB':
                mysql_type = 'BLOB'
            else:
                mysql_type = col_type
            
            line = f"    {col_name} {mysql_type}"
            
            if pk:
                line += " PRIMARY KEY"
            if not_null and not pk:
                line += " NOT NULL"
            if default_val is not None:
                line += f" DEFAULT {default_val}"
            
            if i < len(columns) - 1:
                line += ","
            
            print(line)
        
        print(");")
        print()

if __name__ == "__main__":
    get_schema()
