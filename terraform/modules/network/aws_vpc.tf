# Provides a VPC resource
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc
resource "aws_vpc" "vpc" {

  # (Optional) Region where this resource will be managed.
  region = var.region

  # (Optional) The IPv4 CIDR block for the VPC.
  cidr_block = var.cidr

  # (Optional) A boolean flag to enable/disable DNS hostnames in the VPC.
  enable_dns_hostnames = false

  # (Optional) A map of tags to assign to the resource
  tags = {

    # Naming the VPC for easier identification
    Name = "${var.name}"

    # Module name
    Module = "network"
  }
}

output "vpc_id" {

  # Outputting the ID of the created VPC for external reference
  value = aws_vpc.vpc.id
}

output "vpc_name" {

  # Outputting the ID of the created VPC for external reference
  value = aws_vpc.vpc.tags["Name"]
}

output "cidr_block" {
  value = aws_vpc.vpc.cidr_block
}