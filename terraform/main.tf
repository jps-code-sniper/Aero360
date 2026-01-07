# Bucket de Cloud Storage - Landing Zone
# Aquí llegan los archivos JSON crudos de vuelos antes de procesarse
resource "google_storage_bucket" "landing_zone" {
  name          = "${var.project_id}-vuelos-landing"
  location      = "US"
  force_destroy = true

  # Aplicamos los labels comunes definidos en tags.tf
  labels = local.common_labels
}

# Dataset de BigQuery - Almacén de datos analíticos
# Contiene las tablas raw y transformadas para consultas
resource "google_bigquery_dataset" "airline_dataset" {
  dataset_id    = var.dataset_id
  friendly_name = "Dataset de vuelos Aero360"
  description   = "Datos de vuelos para análisis operacional"
  location      = "US"

  # Las tablas expiran automáticamente a los 30 días (cost management)
  # 2,592,000,000 ms = 30 días
  default_table_expiration_ms = 2592000000

  # Aplicamos los labels comunes
  labels = local.common_labels
}