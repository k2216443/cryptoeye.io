# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table
resource "aws_route_table" "rt-public" {
  # (Required) The VPC ID.
  vpc_id = aws_vpc.vpc.id

  # (Optional) Region where this resource will be managed. Defaults to the Region set in the provider configuration.
  region = var.region

  # (Optional) A list of route objects. Their keys are documented below. This argument is processed in attribute-as-blocks mode.
  # This means that omitting this argument is interpreted as ignoring any existing routes. To remove all managed routes an empty
  # list should be specified.
  route {
    # (Required) The CIDR block of the route.
    cidr_block = "0.0.0.0/0"

    # (Optional) Identifier of a VPC internet gateway, virtual private gateway
    gateway_id = aws_internet_gateway.igw.id
  }

  # (Optional) A map of tags to assign to the resource. If configured with a provider default_tags configuration block present,
  # tags with matching keys will overwrite those defined at the provider-level.
  tags = {
    # Naming convention for the 1st public route table
    "Name" : "${var.name}"

    # Module name
    "Module" : "network"

  }
}

output "rt" {
  value = aws_route_table.rt-public.id
}

