# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table_association
resource "aws_route_table_association" "rta-public-0" {

  # (Optional) Region where this resource will be managed. Defaults to the Region set in the provider configuration.
  region = var.region

  # (Optional) The subnet ID to create an association. Conflicts with gateway_id
  subnet_id = aws_subnet.subnet-public-0.id

  # (Optional) The gateway ID to create an association. Conflicts with subnet_id
  # gateway_id = 

  # (Required) The ID of the routing table to associate with.
  route_table_id = aws_route_table.rt-public-0.id
}

# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table_association
resource "aws_route_table_association" "rta-public-1" {

  # (Optional) Region where this resource will be managed. Defaults to the Region set in the provider configuration.
  region = var.region

  # (Optional) The subnet ID to create an association. Conflicts with gateway_id
  subnet_id = aws_subnet.subnet-public-1.id

  # (Optional) The gateway ID to create an association. Conflicts with subnet_id
  # gateway_id = 

  # (Required) The ID of the routing table to associate with.
  route_table_id = aws_route_table.rt-public-1.id
}
