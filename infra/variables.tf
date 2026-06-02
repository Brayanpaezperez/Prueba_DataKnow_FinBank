# infra/variables.tf

variable "location" {
  description = "Región principal de despliegue en Azure"
  type        = string
  default     = "eastus"
}

variable "prefix" {
  description = "Prefijo base para la nomenclatura de los recursos"
  type        = string
  default     = "finbank"
}