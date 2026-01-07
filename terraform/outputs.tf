# Outputs de Terraform
# Expone valores útiles para scripts de automatización y otros módulos

output "bucket_name" {
  description = "Nombre del bucket de landing zone"
  value       = google_storage_bucket.landing_zone.name
}

output "bucket_url" {
  description = "URL del bucket para usar en scripts"
  value       = "gs://${google_storage_bucket.landing_zone.name}"
}

output "dataset_id" {
  description = "ID del dataset de BigQuery"
  value       = google_bigquery_dataset.airline_dataset.dataset_id
}

output "dataset_full_id" {
  description = "ID completo del dataset (project.dataset)"
  value       = "${var.project_id}.${google_bigquery_dataset.airline_dataset.dataset_id}"
}
