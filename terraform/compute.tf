
locals {
  cloud_init_content = templatefile("${path.module}/userdata/bootstrap.tftpl", {})
  ads                = data.oci_identity_availability_domains.ads.availability_domains
}

data "oci_core_images" "ol8_images" {
  compartment_id           = var.compartment_ocid
  shape                    = var.instance_shape
  operating_system         = "Oracle Linux"
  operating_system_version = "8"
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

resource "oci_core_instance" "instance_ollama" {
  availability_domain = lookup(local.ads[0], "name")
  compartment_id      = var.compartment_ocid
  display_name        = "ollama${var.project_name}${local.deploy_id}"
  shape               = var.instance_shape

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data           = base64encode(local.cloud_init_content)
  }

  shape_config {
    ocpus         = 1
    memory_in_gbs = 32
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.public_subnet.id
    assign_public_ip = true
    display_name     = "ollama${var.project_name}${local.deploy_id}"
    hostname_label   = "ollama${var.project_name}${local.deploy_id}"
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.ol8_images.images[0].id
  }

  timeouts {
    create = "60m"
  }
}

resource "time_sleep" "wait_for_instance" {
  depends_on      = [oci_core_instance.instance_ollama]
  create_duration = "2m"
}
