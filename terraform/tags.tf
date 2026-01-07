# Tags comunes para todos los recursos del proyecto
# Facilita la organización, búsqueda y asignación de costos en GCP

locals {
  # Tags que se aplican a todos los recursos
  common_labels = {
    proyecto   = "aero360"
    ambiente   = "dev"
    equipo     = "dataops"
    gestionado = "terraform"
    owner      = "usuario"
  }

  # Nombre base para recursos (evita repetición)
  nombre_proyecto = "aero360"
}
