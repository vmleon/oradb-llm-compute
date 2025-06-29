terraform {
  required_providers {
    oci = {
      source                = "oracle/oci"
      version               = "~> 6.35"
      configuration_aliases = [oci.home]
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.5.1"
      # https://registry.terraform.io/providers/hashicorp/local/
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3"
      # https://registry.terraform.io/providers/hashicorp/random/
    }
    archive = {
      source  = "hashicorp/archive"
      version = "2.4.2"
    }
  }
}