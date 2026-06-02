# Arquitectura Data Lakehouse - FinBank Core

## 1. Descripción del Proyecto
Este repositorio contiene la implementación de un pipeline de datos end-to-end diseñado bajo la Arquitectura Medallón (Bronze, Silver, Gold). El objetivo es procesar datos transaccionales y de clientes del banco, garantizando altos estándares de calidad, resiliencia y optimización para el consumo analítico.

## 2. Consideraciones Técnicas Transversales
El pipeline ha sido diseñado para cumplir con los requerimientos empresariales en todas sus capas:
* **Idempotencia:** Se implementaron escrituras particionadas y modos de sobreescritura (`overwrite`) nativos de Delta Lake, garantizando que múltiples ejecuciones no dupliquen los registros y se mantenga la integridad.
* **Manejo de Errores (Resiliencia):** Se aplicó el patrón de diseño `try-except` encapsulando la lógica de procesamiento individual de cada tabla. Esto permite capturar fallos de infraestructura, emitir trazas de error y enviar estados de salida (`SUCCESS`/`FAILED`) al orquestador sin interrumpir tareas independientes ni corromper el almacenamiento.
* **Dead Letter Queue (Cuarentena):** Las violaciones de integridad referencial (ej. movimientos financieros asociados a un cliente inexistente) no rompen el pipeline, sino que son aisladas y desviadas automáticamente a una tabla de cuarentena (`ERR_MOVIMIENTOS`) para su posterior auditoría.

## 3. Capas de la Arquitectura

### 3.1. Capa Bronze (Ingesta Cruda)
* **Proceso:** Lectura de archivos Parquet desde zona *landing*.
* **Transformación:** Inyección de metadatos de trazabilidad (`ingest_timestamp`, `batch_id`, `source_system`).
* **Almacenamiento:** Formato Delta, particionado lógicamente por año, mes y día de ingesta para facilitar el reprocesamiento temporal.

### 3.2. Capa Silver (Limpieza y Estandarización)
* **Proceso:** Desduplicación, tipado de datos y aplicación de reglas de negocio restrictivas.
* **Protección PII (Data Governance):** Enmascaramiento mediante hash criptográfico (SHA-256) de información sensible, incluyendo nombres completos y documentos de identidad de los clientes.
* **Observabilidad (Data Quality):** Ejecución de 5 pruebas automatizadas programáticas al finalizar la escritura (Unicidad, Completitud, Validez de Montos, Integridad Referencial y Consistencia de Fechas). *Ver evidencias de calidad en la carpeta `/docs`*.

### 3.3. Capa Gold (Modelado Dimensional)
* **Proceso:** Construcción de modelos de agregación (Visión 360, Canales de Adquisición, Resumen Temporal) y KPIs ejecutivos orientados al consumo directo de herramientas de BI.
* **Optimización:** Tablas particionadas por dimensiones de análisis frecuentes y clústerizadas internamente utilizando el comando `Z-ORDER BY` de Delta Lake para maximizar el rendimiento de las consultas de lectura.

## 4. Linaje de Datos (Data Lineage) - Capa Gold
A continuación se documenta la trazabilidad de tres campos calculados críticos construidos en la capa Gold para responder a las necesidades del negocio:

**Campo Calculado 1: `total_monto_transaccionado`**
* **Tabla de Origen:** `Silver.TB_MOV_FINANCIEROS`
* **Columna de Origen:** `vr_mov`
* **Transformación Aplicada:** Agregación sumatoria (`sum()`) agrupada por la llave `id_cli` y redondeada a dos decimales.
* **Propósito:** Identificar el valor monetario histórico movido por cliente, permitiendo crear modelos de segmentación, fidelización o scoring de riesgo transaccional.

**Campo Calculado 2: `volumen_monetario_canal`**
* **Tabla de Origen:** `Gold.AGG_PERFIL_CLIENTE` (derivada temporalmente de Silver).
* **Columna de Origen:** `total_monto_transaccionado`
* **Transformación Aplicada:** Agregación sumatoria (`sum()`) de los montos consolidados, agrupada por la dimensión `canal_adquis`.
* **Propósito:** Calcular el ROI y el impacto transaccional de cada canal de adquisición (Sucursal vs. App) para guiar la estrategia comercial y de marketing.

**Campo Calculado 3: `kpi_ticket_promedio`**
* **Tabla de Origen:** `Silver.TB_MOV_FINANCIEROS`
* **Columna de Origen:** `vr_mov`
* **Transformación Aplicada:** Función de promedio matemático (`avg()`) sobre la totalidad de los registros válidos, redondeado a dos decimales.
* **Propósito:** Alimentar la tabla plana `KPI_EJECUTIVO_FINANCIERO`. Permite a la gerencia monitorear diariamente de forma macroeconómica el tamaño promedio de las transacciones del banco.
## 5. Despliegue de Infraestructura (Terraform)
La infraestructura base necesaria para la ejecución de este pipeline se gestiona mediante Infraestructura como Código (IaC) utilizando Terraform.

**Requisitos previos:**
* Terraform >= 1.0 instalado localmente.
* CLI del proveedor Cloud autenticado (ej. Azure CLI).

**Pasos para el despliegue:**
1. Navegar al directorio de infraestructura:
   ```bash
   cd terraform/
   ```
2. Inicializar el directorio y descargar los providers:
Descargue los proveedores necesarios (AzureRM):
   ```bash
   terraform init
   ```
3. Planificar el despliegue (Opcional pero recomendado):
Valide los recursos que se van a crear sin afectar la nube:
   ```bash
   terraform plan
   ```
4. Aplicar la infraestructura:
Ejecute el despliegue oficial y confirme con yes cuando se le solicite:
   ```bash
   terraform apply
   ```

## Lista de recursos 
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


## 6. Instrucciones de Ejecución y Orquestación
El pipeline completo consta de 4 cuadernos ubicados en la carpeta `/pipelines`, diseñados para ejecutarse secuencialmente mediante un orquestador formal (Databricks Workflows) recibiendo dinámicamente el `batch_id`:

1. `00_Source_to_Bronze`: Ingesta inicial desde landing con inyección de metadatos.
2. `01_Bronze_to_Silver`: Limpieza, calidad (DQ) y desvío a cuarentena (Depende de Bronze).
3. `02_Silver_to_Gold`: Aplicación de reglas de negocio y optimización dimensional (Depende de Silver).
4. `03_Reporte_Final`: Cálculo de volumetrías totales y envío de resumen gerencial (Depende de Gold).

### 6.1. Políticas del Orquestador (Infraestructura como Código)
Para cumplir con los requerimientos de resiliencia y monitoreo, el flujo está gobernado por políticas estrictas. La definición completa del DAG se encuentra exportada en formato JSON en la ruta `/orchestration/databricks_job_config.json`.

* **Ejecución Programada (Cron):** Configurado para ejecutarse diariamente y de forma desatendida a las **02:00 AM (Huso horario local: America/Bogota)**.
* **Tolerancia a Fallos:** Cada tarea cuenta con un máximo de **3 reintentos automáticos** configurados con un **backoff exponencial** (o un *delay* equivalente según el nivel de suscripción) para permitir la recuperación de la infraestructura, y un *timeout* estricto de 30 minutos por tarea para evitar costos excesivos de cómputo.
* **Sistema de Notificaciones:**
  * Alertas nativas del sistema enviadas por correo electrónico en caso de fallo crítico (indicando nombre del DAG, tarea fallida, hora exacta y enlace al log).
  * Ejecución exitosa coronada por el script `03_Reporte_Final`, el cual emite un resumen detallando el número de registros procesados por capa, el tiempo total de ejecución y las métricas de la tabla de cuarentena.

## 7. Estructura del Repositorio
El proyecto mantiene la siguiente jerarquía de archivos para separar el código fuente, la configuración de despliegue y las evidencias de validación:

```text
/
├── README.md
├── orchestration/
│   └── databricks_job_config.json      <-- Configuración del DAG y políticas del orquestador
├── pipelines/
│   ├── 00_Source_to_Bronze.py
│   ├── 01_Bronze_to_Silver.py
│   ├── 02_Silver_to_Gold.py
│   └── 03_Reporte_Final.py             <-- Generador del reporte de éxito
├── docs/
│   ├── dq_silver.png                   <-- Evidencia: 5 Pruebas de calidad en Silver (Passed)
│   ├── error_cuarentena.png            <-- Evidencia: Dead Letter Queue (Violación referencial)
│   └── reconciliacion_gold.png         <-- Evidencia: Cuadre financiero y metadatos Z-Order
└── scripts_origen/
    ├── load_to_sql.py                  <-- Script de extracción original
    └── contexto_ingesta.txt            <-- Contexto de la carga a landing