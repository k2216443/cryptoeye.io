
# Provides an VPC subnet resource.
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet
resource "aws_subnet" "subnet" {
  # (Optional) Region where this resource will be managed. Defaults to the Region set in the provider configuration.
  region = var.region

  # (Optional) Specify true to indicate that network interfaces created in the specified subnet should be assigned an IPv6 address.
  assign_ipv6_address_on_creation = false

  # VPC ID where the subnet is created
  vpc_id = aws_vpc.vpc.id

  # (Optional) The IPv4 CIDR block for the subnet
  cidr_block = var.cidr

  # (Optional) Indicates whether DNS queries made to the Amazon-provided DNS Resolver in this subnet should return synthetic IPv6 addresses for IPv4-only destinations.
  enable_dns64 = false

  # (Optional) AZ for the subnet.
  availability_zone = "${var.region}a"

  # (Optional) Specify true to indicate that instances launched into the subnet should be assigned a public IP address
  map_public_ip_on_launch = true

  # (Optional) The type of hostnames to assign to instances in the subnet at launch.
  private_dns_hostname_type_on_launch = "resource-name"

  # (Optional) A map of tags to assign to the resource.
  tags = {

    # Naming convention for the 1st public subnet
    Name = "${var.name}"

    Module = "network"
  }
}

output "subnet" {
  value = aws_subnet.subnet.id
}

output "subnet_name" {
  value = aws_subnet.subnet.tags["Name"]
}
