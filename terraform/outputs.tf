output "deployment" {
  value = "${local.project_name}${local.deploy_id}"
}

output "ollama_private_ip" {
  value = oci_core_instance.instance_ollama.private_ip
}