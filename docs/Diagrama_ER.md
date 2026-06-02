# Diagrama Entidad-Relación - FinBank S.A.

A continuación se presenta el modelo relacional del sistema origen (Core Bancario), donde se evidencia la integridad referencial entre los clientes, productos y sus respectivas transacciones.

```mermaid
erDiagram
    TB_CLIENTES_CORE {
        string id_cli PK
        string nomb_cli
        string apell_cli
        string tip_doc
        string num_doc
        date fec_nac
    }
    TB_PRODUCTOS_CAT {
        string cod_prod PK
        string desc_prod
        string tip_prod
        float tasa_ea
    }
    TB_SUCURSALES_RED {
        string Cod_suc PK
        string nom_suc
        string tip_punto
        string ciudad
    }
    TB_MOV_FINANCIEROS {
        string id_mov PK
        string id_cli FK
        string cod_prod FK
        float vr_mov
        string tip_mov
    }
    TB_OBLIGACIONES {
        string id_oblig PK
        string id_cli FK
        string cod_prod FK
        float vr_aprobado
        int dias_mora_act
    }
    TB_COMISIONES_LOG {
        string id_comision PK
        string id_cli FK
        string cod_prod FK
        float vr_comision
    }

    TB_CLIENTES_CORE ||--o{ TB_MOV_FINANCIEROS : "realiza"
    TB_CLIENTES_CORE ||--o{ TB_OBLIGACIONES : "adquiere"
    TB_CLIENTES_CORE ||--o{ TB_COMISIONES_LOG : "paga"
    
    TB_PRODUCTOS_CAT ||--o{ TB_MOV_FINANCIEROS : "registra"
    TB_PRODUCTOS_CAT ||--o{ TB_OBLIGACIONES : "asociado_a"
    TB_PRODUCTOS_CAT ||--o{ TB_COMISIONES_LOG : "genera"