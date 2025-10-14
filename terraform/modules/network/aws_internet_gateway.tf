# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/internet_gateway
resource "aws_internet_gateway" "igw" {

  # (Optional) The VPC ID to create in. See the aws_internet_gateway_attachment resource for an alternate way to attach an Internet Gateway to a VPC.
  vpc_id = aws_vpc.vpc.id

  # (Optional) Region where this resource will be managed. Defaults to the Region set in the provider configuration.
  region = var.region

  # (Optional) A map of tags to assign to the resource. If configured with a provider default_tags configuration block present,
  # tags with matching keys will overwrite those defined at the provider-level.
  tags = {
    Name   = "${var.name}"
    Module = "network"
  }
}
