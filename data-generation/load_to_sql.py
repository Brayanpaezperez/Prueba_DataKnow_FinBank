import pandas as pd
from sqlalchemy import create_engine, text
import os
import urllib

# 1. Configuración de Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_CSV = os.path.join(BASE_DIR, 'output', 'csv')

# 2. Credenciales de Azure SQL
server = os.getenv('AZURE_SQL_SERVER')
database = os.getenv('AZURE_SQL_DATABASE')
username = os.getenv('AZURE_SQL_USER')
password = os.getenv('AZURE_SQL_PASSWORD')
driver = '{ODBC Driver 17 for SQL Server}'

# Formatear la cadena de conexión para SQLAlchemy
odbc_str = f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'
connect_str = f'mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(odbc_str)}'

# fast_executemany=True es VITAL para que Pandas haga bulk inserts a Azure rápidamente
engine = create_engine(connect_str, fast_executemany=True)

tablas = [
    'TB_PRODUCTOS_CAT',
    'TB_CLIENTES_CORE',
    'TB_SUCURSALES_RED',
    'TB_OBLIGACIONES',
    'TB_COMISIONES_LOG',
    'TB_MOV_FINANCIEROS'
]

if __name__ == "__main__":
    print("🚀 Iniciando carga a Azure SQL Database...")
    
    # 3. Carga de datos
    for tabla in tablas:
        csv_path = os.path.join(DIR_CSV, f'{tabla}.csv')
        print(f"Leyendo {tabla} con Pandas...")
        df = pd.read_csv(csv_path)
        
        print(f"Subiendo {len(df)} registros a la nube...")
        # chunksize=10000 asegura que la BD Basic no colapse por recibir todo de golpe
        df.to_sql(tabla, con=engine, index=False, if_exists='replace', chunksize=10000)
        print(f"✅ {tabla} cargada exitosamente.")

    print("\n--- EVIDENCIA DE CARGA AZURE SQL (SELECT COUNT(*)) ---")
    
    # 4. Generación de Evidencias
    with engine.connect() as conn:
        for tabla in tablas:
            query = text(f"SELECT COUNT(*) FROM {tabla}")
            result = conn.execute(query).scalar()
            print(f"Tabla: {tabla.ljust(20)} | Registros en Azure: {result}")
            
    print("Fase de Ingesta SQL completada.")