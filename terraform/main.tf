locals {
  project_name = var.project_name
  deploy_id    = random_string.deploy_id.result
  anywhere     = "0.0.0.0/0"
  tcp          = "6"
}


resource "random_string" "deploy_id" {
  length  = 2
  special = false
  upper   = false
}
