resource "oci_core_virtual_network" "vcn" {
  compartment_id = var.compartment_ocid
  cidr_blocks    = ["10.0.0.0/16"]
  display_name   = "VCN ${local.project_name} ${local.deploy_id}"
  dns_label      = "vcn${local.project_name}${local.deploy_id}"
}

resource "oci_core_service_gateway" "service_gateway" {
  compartment_id = var.compartment_ocid
  display_name   = "service_gateway"
  vcn_id         = oci_core_virtual_network.vcn.id
  services {
    service_id = data.oci_core_services.all_services.services[0].id
  }
}

resource "oci_core_internet_gateway" "ig" {
  compartment_id = var.compartment_ocid
  display_name   = "ig_${local.project_name}_${local.deploy_id}"
  vcn_id         = oci_core_virtual_network.vcn.id
}

resource "oci_core_nat_gateway" "nat_gateway" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_virtual_network.vcn.id
  display_name   = "nat_${local.project_name}_${local.deploy_id}"
}

resource "oci_core_default_route_table" "default_route_table" {
  manage_default_resource_id = oci_core_virtual_network.vcn.default_route_table_id
  display_name               = "DefaultRouteTable"

  route_rules {
    destination       = local.anywhere
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.ig.id
  }
}

resource "oci_core_route_table" "route_private" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_virtual_network.vcn.id
  display_name   = "route_private"

  route_rules {
    destination       = local.anywhere
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_nat_gateway.nat_gateway.id
  }
}

resource "oci_core_subnet" "public_subnet" {
  cidr_block                 = "10.0.1.0/24"
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_virtual_network.vcn.id
  display_name               = "public_subnet_${local.project_name}_${local.deploy_id}"
  dns_label                  = "public"
  prohibit_public_ip_on_vnic = false
  security_list_ids = [
    oci_core_virtual_network.vcn.default_security_list_id,
    oci_core_security_list.public_ollama_seclist.id
  ]
  route_table_id  = oci_core_virtual_network.vcn.default_route_table_id // TODO check this route_private or default?
  dhcp_options_id = oci_core_virtual_network.vcn.default_dhcp_options_id
}

resource "oci_core_subnet" "private_subnet" {
  cidr_block                 = "10.0.3.0/24"
  compartment_id             = var.compartment_ocid
  vcn_id                     = oci_core_virtual_network.vcn.id
  display_name               = "private_subnet_${local.project_name}_${local.deploy_id}"
  dns_label                  = "private"
  prohibit_public_ip_on_vnic = true
  security_list_ids = [
    oci_core_virtual_network.vcn.default_security_list_id
  ]
  route_table_id  = oci_core_route_table.route_private.id // TODO check this route_private or default?
  dhcp_options_id = oci_core_virtual_network.vcn.default_dhcp_options_id
}

resource "oci_core_security_list" "public_ollama_seclist" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_virtual_network.vcn.id
  display_name   = "Public HTTP Security List"

  ingress_security_rules {
    protocol  = local.tcp
    source    = local.anywhere
    stateless = false

    tcp_options {
      min = 11434
      max = 11434
    }
  }

}