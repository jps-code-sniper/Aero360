terraform {
  backend "gcs" {
    bucket  = "aero360-482417-tfstate"
    prefix  = "terraform/state"
  }
}