# AWS Internet Gateway - Provides a resource to create a VPC Internet Gateway for public internet connectivity
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/internet_gateway

resource "aws_internet_gateway" "igw" {

  # Optional: The VPC ID to create in
  vpc_id = aws_vpc.vpc.id

  # Optional: Region where this resource will be managed
  region = var.region

  # Optional: A map of tags to assign to the resource
  tags = {
    Name   = "${var.name}"
    Module = "network"
  }
}
