# 📖 Catálogo de Datos - FinBank Core

Este catálogo documenta las estructuras de datos certificadas a partir de la capa Silver y Gold, estableciendo la clasificación de privacidad (PII) y el tipo de dato.

## 🛡️ Capa Silver (Datos Estructurados y Protegidos)

### Tabla: `Silver.TB_CLIENTES_CORE`
Contiene la información demográfica y de estado de los clientes. Los datos sensibles han sido anonimizados mediante Hashing (SHA-256).

| Campo | Tipo de Dato | Origen (Bronze) | Contiene PII | Tratamiento de Privacidad |
| :--- | :--- | :--- | :---: | :--- |
| `id_cli` | String | `id_cliente` | ⚠️ Sí | Cifrado unidireccional (SHA-256) aplicado. |
| `nombre_completo` | String | `nombre` | ⚠️ Sí | Enmascaramiento / Hash aplicado. |
| `fecha_nacimiento` | Date | `f_nacimiento` | No | Casteo a Date. |
| `canal_adquis` | String | `canal_ingreso` | No | Limpieza de nulos. |
| `estado_cli` | String | `status` | No | Estandarizado (Activo/Inactivo). |

### Tabla: `Silver.TB_MOV_FINANCIEROS`
Registra la transaccionalidad a nivel de ítem. Sometida a reglas de Data Quality y validación referencial.

| Campo | Tipo de Dato | Origen (Bronze) | Contiene PII | Tratamiento de Privacidad |
| :--- | :--- | :--- | :---: | :--- |
| `id_transaccion` | String | `tx_id` | No | N/A |
| `id_cli` | String | `cliente_id` | ⚠️ Sí | Cruce referencial con tabla de clientes (Hash). |
| `vr_mov` | Decimal(18,2)| `monto` | No | Casteo numérico estricto. |
| `fecha_tx` | Timestamp | `fecha` | No | Estandarización de formato. |

## 🥇 Capa Gold (Modelos Dimensionales)

### Tabla: `Gold.AGG_PERFIL_CLIENTE`
| Campo | Tipo de Dato | Origen Lógico | Propósito de Negocio |
| :--- | :--- | :--- | :--- |
| `id_cli` | String | `Silver.TB_MOV_FINANCIEROS` | Llave foránea del cliente (Hash). |
| `total_monto_transaccionado`| Decimal(18,2) | Cálculo Sumatorio | KPI: Valor histórico movido por el usuario. |
| `cantidad_movimientos` | Integer | Conteo | KPI: Frecuencia de uso del cliente. |
| `canal_adquis` | String | `Silver.TB_CLIENTES_CORE`| Dimensión de segmentación de marketing. |