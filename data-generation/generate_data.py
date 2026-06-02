import pandas as pd
import numpy as np
from faker import Faker
import yaml
import os
import random


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, 'config.yaml') 
print(CONFIG_PATH)

with open(CONFIG_PATH, 'r') as file:
    config = yaml.safe_load(file)


SEED = config['seed']
Faker.seed(SEED)
np.random.seed(SEED)
random.seed(SEED)
fake = Faker('es_CO')

def generate_productos_cat(n):
    """Genera TB_PRODUCTOS_CAT (Mínimo 50 registros)"""
    familias = ['Crédito', 'Ahorro', 'Transaccional']
    productos = []
    
    for i in range(1, n + 1):
        tip_prod = np.random.choice(familias, p=[0.4, 0.4, 0.2])
        productos.append({
            'cod_prod': f'PRD-{str(i).zfill(4)}',
            'desc_prod': f'{tip_prod} {fake.word().capitalize()}',
            'tip_prod': tip_prod,
            'tasa_ea': round(np.random.uniform(0.01, 0.28), 4) if tip_prod == 'Crédito' else round(np.random.uniform(0.0, 0.05), 4),
            'plazo_max_meses': int(np.random.choice([12, 24, 36, 48, 60, 0])),
            'cuota_min': round(np.random.uniform(10000, 50000), 2),
            'comision_admin': round(np.random.uniform(0, 15000), 2),
            'estado_prod': np.random.choice(['Activo', 'Inactivo'], p=[0.9, 0.1])
        })
    return pd.DataFrame(productos)

def generate_clientes_core(n):
    """Genera TB_CLIENTES_CORE (Mínimo 10.000 registros)"""
    clientes = []
    segmentos = ['Basico', 'Estandar', 'Premium', 'Elite']
    

    departamentos = ['Bogota D.C.', 'Antioquia', 'Valle del Cauca', 'Atlantico', 'Santander', 'Cundinamarca', 'Bolivar']
    prob_deptos = [0.35, 0.20, 0.15, 0.10, 0.10, 0.05, 0.05] # Mayor concentración en ciudades principales

    for i in range(1, n + 1):
        clientes.append({
            'id_cli': f'CLI-{str(i).zfill(6)}',
            'nomb_cli': fake.first_name(),
            'apell_cli': fake.last_name(),
            'tip_doc': np.random.choice(['CC', 'CE', 'Pasaporte'], p=[0.9, 0.08, 0.02]),
            'num_doc': fake.unique.random_number(digits=10, fix_len=True),
            'fec_nac': fake.date_of_birth(minimum_age=18, maximum_age=80),
            'fec_alta': fake.date_between_dates(date_start=pd.to_datetime(config['start_date']), date_end=pd.to_datetime(config['end_date'])),
            'cod_segmento': np.random.choice(segmentos, p=[0.5, 0.3, 0.15, 0.05]),
            'score_buro': int(np.random.normal(loc=650, scale=100)), # Distribución normal realista
            'ciudad_res': fake.city(),
            'depto_res':np.random.choice(departamentos, p=prob_deptos),
            'estado_cli': np.random.choice(['Activo', 'Inactivo', 'Bloqueado'], p=[0.85, 0.1, 0.05]),
            'canal_adquis': np.random.choice(['App', 'Web', 'Sucursal', 'Referido'])
        })
    
    df = pd.DataFrame(clientes)
    
    
    mask = np.random.rand(len(df)) < 0.05
    df.loc[mask, 'canal_adquis'] = np.nan
    
    
    df.loc[0, 'fec_nac'] = pd.to_datetime('2050-01-01') 
    df['fec_nac'] = pd.to_datetime(df['fec_nac'])
    df['fec_alta'] = pd.to_datetime(df['fec_alta'])
    
    return df

def generate_sucursales_red(n):
    """Genera TB_SUCURSALES_RED (Mínimo 200 registros)"""
    sucursales = []
    departamentos = ['Bogota D.C.', 'Antioquia', 'Valle del Cauca', 'Atlantico', 'Santander', 'Cundinamarca', 'Bolivar']
    
    for i in range(1, n + 1):
        sucursales.append({
            'Cod_suc': f'SUC-{str(i).zfill(3)}',
            'nom_suc': f'Sucursal {fake.city()}',
            'tip_punto': np.random.choice(['Oficina', 'Corresponsal', 'Cajero ATM']),
            'ciudad': fake.city(),
            'depto': np.random.choice(departamentos), 
            'latitud': float(fake.latitude()),
            'longitud': float(fake.longitude()),
            'activo': np.random.choice([1, 0], p=[0.95, 0.05])
        })
    return pd.DataFrame(sucursales)

def generate_obligaciones(n, df_clientes, df_productos):
    """Genera TB_OBLIGACIONES (Mínimo 30.000 registros)"""
    
    prod_credito = df_productos[df_productos['tip_prod'] == 'Crédito']['cod_prod'].values
    clientes_ids = df_clientes['id_cli'].values
    
    df = pd.DataFrame({
        'id_oblig': [f'OBL-{str(i).zfill(6)}' for i in range(1, n + 1)],
        'id_cli': np.random.choice(clientes_ids, n),
        'cod_prod': np.random.choice(prod_credito, n),
        'vr_aprobado': np.random.uniform(1000000, 50000000, n).round(2),
        'fec_desembolso': [fake.date_between(start_date='-2y', end_date='today') for _ in range(n)]
    })
    
    df['vr_desembolsado'] = df['vr_aprobado']
    df['sdo_capital'] = (df['vr_aprobado'] * np.random.uniform(0.1, 0.9, n)).round(2)
    df['vr_cuota'] = (df['vr_aprobado'] * 0.05).round(2)
    df['fec_desembolso'] = pd.to_datetime(df['fec_desembolso'])
    df['fec_venc'] = df['fec_desembolso'] + pd.to_timedelta(np.random.randint(30, 365, n), unit='D')
    df['dias_mora_act'] = np.random.choice([0, 15, 45, 75, 120], n, p=[0.7, 0.15, 0.08, 0.05, 0.02])
    df['num_cuotas_pend'] = np.random.randint(1, 60, n)
    df['calif_riesgo'] = np.random.choice(['A', 'B', 'C', 'D', 'E'], n, p=[0.6, 0.2, 0.1, 0.05, 0.05])
    
    return df

def generate_movimientos(n, df_clientes, df_productos):
    """Genera TB_MOV_FINANCIEROS usando NumPy para máximo rendimiento (500.000 registros)"""
    clientes_ids = df_clientes['id_cli'].values
    productos_ids = df_productos['cod_prod'].values
    
   
    mitad_1 = np.random.randint(10000, 99999, n).astype(str)
    mitad_2 = np.random.randint(10000, 99999, n).astype(str)
    
    df = pd.DataFrame({
        'id_mov': [f'MOV-{str(i).zfill(7)}' for i in range(1, n + 1)],
        'id_cli': np.random.choice(clientes_ids, n),
        'cod_prod': np.random.choice(productos_ids, n),
        'num_cuenta': mitad_1 + mitad_2, # Concatenación segura de 10 dígitos
        'fec_mov': [fake.date_between(start_date='-1y', end_date='today') for _ in range(n)]
    })
    
    df['fec_mov'] = pd.to_datetime(df['fec_mov'])
    df['hra_mov'] = [f"{str(random.randint(0,23)).zfill(2)}:{str(random.randint(0,59)).zfill(2)}:00" for _ in range(n)]
    df['vr_mov'] = np.random.uniform(10000, 5000000, n).round(2)
    df['tip_mov'] = np.random.choice(['Pago', 'Transferencia', 'Retiro', 'Consignacion'], n)
    df['cod_canal'] = np.random.choice(['App', 'Web', 'ATM', 'Oficina'], n)
    df['cod_ciudad'] = np.random.randint(1, 100, n).astype(str)
    df['cod_estado_mov'] = np.random.choice(['Exitoso', 'Rechazado', 'Pendiente'], n, p=[0.9, 0.08, 0.02])
    df['id_dispositivo'] = [fake.uuid4()[:8] for _ in range(n)]
    
    
    mask_anomalia = np.random.rand(n) < 0.01
    df.loc[mask_anomalia, 'vr_mov'] = 0.0
    
    return df

def generate_comisiones(n, df_clientes, df_productos):
    """Genera TB_COMISIONES_LOG (Mínimo 80.000 registros)"""
    clientes_ids = df_clientes['id_cli'].values
    productos_ids = df_productos['cod_prod'].values
    
    df = pd.DataFrame({
        'id_comision': [f'COM-{str(i).zfill(6)}' for i in range(1, n + 1)],
        'id_cli': np.random.choice(clientes_ids, n),
        'cod_prod': np.random.choice(productos_ids, n),
        'fec_cobro': [fake.date_between(start_date='-1y', end_date='today') for _ in range(n)]
    })
    
    df['fec_cobro'] = pd.to_datetime(df['fec_cobro'])
    df['vr_comision'] = np.random.uniform(5000, 25000, n).round(2)
    df['tip_comision'] = np.random.choice(['Manejo', 'Transferencia', 'Retiro ATM'], n)
    df['estado_cobro'] = np.random.choice(['Cobrado', 'Pendiente', 'Exonerado'], n, p=[0.8, 0.1, 0.1])
    
    return df

if __name__ == "__main__":
    print("Iniciando generación de datos sintéticos...")
    
    # Dimensiones Maestras
    df_productos = generate_productos_cat(config['volumes']['TB_PRODUCTOS_CAT'])
    df_clientes = generate_clientes_core(config['volumes']['TB_CLIENTES_CORE'])
    df_sucursales = generate_sucursales_red(config['volumes']['TB_SUCURSALES_RED'])
    
    print("Generando transaccionales (Esto puede tardar unos segundos)...")
    # Tablas Transaccionales (Requieren las dimensiones para integridad)
    df_oblig = generate_obligaciones(config['volumes']['TB_OBLIGACIONES'], df_clientes, df_productos)
    df_comis = generate_comisiones(config['volumes']['TB_COMISIONES_LOG'], df_clientes, df_productos)
    df_movs = generate_movimientos(config['volumes']['TB_MOV_FINANCIEROS'], df_clientes, df_productos)
    
    # Guardado
    dir_csv = os.path.join(BASE_DIR, 'output', 'csv')
    dir_parquet = os.path.join(BASE_DIR, 'output', 'parquet')
    os.makedirs(dir_csv, exist_ok=True)
    os.makedirs(dir_parquet, exist_ok=True)
    
    tablas = [
        (df_productos, 'TB_PRODUCTOS_CAT'),
        (df_clientes, 'TB_CLIENTES_CORE'),
        (df_sucursales, 'TB_SUCURSALES_RED'),
        (df_oblig, 'TB_OBLIGACIONES'),
        (df_comis, 'TB_COMISIONES_LOG'),
        (df_movs, 'TB_MOV_FINANCIEROS')
    ]
    
    for df, name in tablas:
        df.to_csv(os.path.join(dir_csv, f'{name}.csv'), index=False)
        df.to_parquet(os.path.join(dir_parquet, f'{name}.parquet'), index=False)
        print(f"Generada tabla {name} - Shape: {df.shape}")
        
    print("🚀 Proceso completado exitosamente.")