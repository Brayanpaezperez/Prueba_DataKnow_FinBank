# infra/main.tf

# 1. Configuración del proveedor de Azure
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }
}

# 2. Identidad 
data "azurerm_client_config" "current" {}



# 3. Resource Group (El contenedor principal)
resource "azurerm_resource_group" "rg" {
  name     = "rg-${var.prefix}-data-dev"
  location = var.location
}

# 4. Storage Account (Data Lake Gen2)
resource "azurerm_storage_account" "datalake" {
  name                     = "st${var.prefix}datalakedev01" 
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true

  tags = {
    environment = "dev"
    project     = "DataKnow-Challenge"
  }
}

# 5. Capas Medallion (Bronze, Silver, Gold)
resource "azurerm_storage_data_lake_gen2_filesystem" "medallion" {
  for_each           = toset(["bronze", "silver", "gold"])
  name               = each.key
  storage_account_id = azurerm_storage_account.datalake.id
}

# 6. Azure Key Vault (Seguridad de Secretos)
resource "azurerm_key_vault" "kv" {
  name                        = "kv-${var.prefix}-dev-01"
  location                    = azurerm_resource_group.rg.location
  resource_group_name         = azurerm_resource_group.rg.name
  enabled_for_disk_encryption = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  soft_delete_retention_days  = 7
  purge_protection_enabled    = false
  sku_name                    = "standard"

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id
    secret_permissions = ["Get", "List", "Set", "Delete", "Recover", "Backup", "Restore"]
  }
}

# 7. Azure Data Factory (Orquestador)
resource "azurerm_data_factory" "adf" {
  name                = "adf-${var.prefix}-dev-01"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  
  identity {
    type = "SystemAssigned"
  }
}

# 8. Log Analytics Workspace (Monitoreo)
resource "azurerm_log_analytics_workspace" "law" {
  name                = "law-${var.prefix}-dev-01"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

# 9. Azure Databricks (Procesamiento PySpark)
resource "azurerm_databricks_workspace" "dbw" {
  name                = "dbw-${var.prefix}-dev-01"
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "trial" # Versión de prueba de 14 días gratuita
}