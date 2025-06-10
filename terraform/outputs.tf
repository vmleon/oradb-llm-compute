output "deployment" {
  value = "${local.project_name}${local.deploy_id}"
}

output "ollama_public_ip" {
  value = oci_core_instance.instance_ollama.public_ip
}