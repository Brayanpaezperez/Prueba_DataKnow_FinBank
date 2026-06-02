# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-06-02
### Added
- **Fase 5 (Gobierno y Seguridad):**
  - Implementación de RBAC con 3 perfiles (Admin, Data Engineer, Data Analyst) mediante Unity Catalog / Databricks ACLs.
  - Alerta programática de anomalía de volumetría (>30% de desviación) inyectada en la transición Bronze-Silver.
  - Creación del Catálogo de Datos (`/docs/Data_Catalog.md`) con clasificación de PII.
- **Fase 4 (Orquestación):**
  - DAG configurado en Databricks Workflows con políticas de *Exponential Backoff* (3 reintentos) y Timeouts de 30 minutos.
  - Reporte diario consolidado de métricas (Script `03_Reporte_Final`).
- **Fase 3 (Transformación y DQ):**
  - Pipeline Medallón completo (Bronze, Silver, Gold) utilizando PySpark y Delta Lake.
  - Cortocircuito de Calidad de Datos (Dead Letter Queue) para aislar registros con violaciones referenciales en `ERR_MOVIMIENTOS`.
  - Optimización física de tablas Gold particionadas y con `Z-ORDER BY`.
- **Fase 2 (Infraestructura):**
  - Aprovisionamiento de Azure Data Lake Storage y configuración base vía Terraform (IaC).
  - Scripts securizados sin credenciales quemadas (`os.getenv`).