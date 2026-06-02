import pandas as pd
from sqlalchemy import create_engine, text
import os

# 1. Configuración de Rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIR_CSV = os.path.join(BASE_DIR, 'output', 'csv')
DB_PATH = os.path.join(BASE_DIR, 'finbank_origen.db')

# 2. Conexión al motor Relacional (SQLite para pruebas locales)
# Para migrar a Azure SQL, solo se cambiaría este string de conexión
engine = create_engine(f'sqlite:///{DB_PATH}')

tablas = [
    'TB_PRODUCTOS_CAT',
    'TB_CLIENTES_CORE',
    'TB_SUCURSALES_RED',
    'TB_OBLIGACIONES',
    'TB_COMISIONES_LOG',
    'TB_MOV_FINANCIEROS'
]

if __name__ == "__main__":
    print("Iniciando carga a la Base de Datos Relacional...")
    
    # 3. Carga de datos
    for tabla in tablas:
        csv_path = os.path.join(DIR_CSV, f'{tabla}.csv')
        print(f"Leyendo {tabla}...")
        df = pd.read_csv(csv_path)
        
        # Insertar en SQL (Reemplaza la tabla si ya existe)
        df.to_sql(tabla, con=engine, index=False, if_exists='replace')
        print(f"✅ {tabla} cargada exitosamente.")

    print("\n--- EVIDENCIA DE CARGA (SELECT COUNT(*)) ---")
    
    # 4. Generación de Evidencias (Requisito de la prueba)
    with engine.connect() as conn:
        for tabla in tablas:
            query = text(f"SELECT COUNT(*) FROM {tabla}")
            result = conn.execute(query).scalar()
            print(f"Tabla: {tabla.ljust(20)} | Registros insertados: {result}")
            
    print("\n🚀 Fase 1 completada al 100%.")