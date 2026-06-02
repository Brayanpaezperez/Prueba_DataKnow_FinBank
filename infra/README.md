# Despliegue de Infraestructura - FinBank Data Platform

Este directorio contiene la Infraestructura como Código (IaC) escrita en Terraform para aprovisionar el ecosistema de datos en Azure, cumpliendo con la arquitectura Medallion.

##  Instrucciones de Despliegue

Siga estos pasos para desplegar la infraestructura en su cuenta de Azure:

1. **Autenticación:**
   Abra la terminal y autentíquese en su cuenta de Azure ejecutando:
   ```bash
   az login
   ```

2. **Inicializar Terraform::**
Descargue los proveedores necesarios (AzureRM):
   ```bash
   terraform init
   ```
3. **Planificar el despliegue:**
Valide los recursos que se van a crear sin afectar la nube:
   ```bash
    terraform plan
   ```
4. **Aplicar la infraestructura:**
Ejecute el despliegue oficial y confirme con yes cuando se le solicite:
   ```bash
    terraform apply
   ```
## Recursos creados

| Recurso | Nombre Asignado | Región | Propósito en la Solución |
| :--- | :--- | :--- | :--- |
| **Resource Group** | `rg-finbank-data-dev` | East US | Contenedor lógico principal que agrupa todos los recursos del proyecto. |
| **Storage Account** | `stfinbankdatalakedev01` | East US | Data Lake Storage Gen2 que alojará los datos en formato Parquet/Delta. |
| **Contenedor (Bronze)** | `bronze` | East US | Capa de datos crudos (Raw Data) del Data Lake. |
| **Contenedor (Silver)** | `silver` | East US | Capa de datos limpios y estandarizados del Data Lake. |
| **Contenedor (Gold)** | `gold` | East US | Capa de datos modelados para consumo analítico y de BI. |
| **Azure Key Vault** | `kv-finbank-dev-01` | East US | Gestión segura de secretos, contraseñas y tokens del proyecto. |
| **Data Factory** | `adf-finbank-dev-01` | East US | Herramienta de orquestación y movimiento de datos (ETL/ELT). |
| **Databricks Workspace** | `dbw-finbank-dev-01` | East US | Entorno de procesamiento masivo en PySpark para transformaciones pesadas. |
| **Log Analytics** | `law-finbank-dev-01` | East US | Monitoreo centralizado y recolección de logs de toda la arquitectura. |