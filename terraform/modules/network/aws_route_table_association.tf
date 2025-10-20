# AWS Route Table Association - Provides a resource to create an association between a route table and a subnet or a route table and an internet gateway or virtual private gateway
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table_association

resource "aws_route_table_association" "rta-public-0" {

  # Optional: Region where this resource will be managed
  region = var.region

  # Optional: The subnet ID to create an association (conflicts with gateway_id)
  subnet_id = aws_subnet.subnet-public-0.id

  # Required: The ID of the routing table to associate with
  route_table_id = aws_route_table.rt-public-0.id
}

# AWS Route Table Association - Provides a resource to create an association between a route table and a subnet or a route table and an internet gateway or virtual private gateway
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table_association

resource "aws_route_table_association" "rta-public-1" {

  # Optional: Region where this resource will be managed
  region = var.region

  # Optional: The subnet ID to create an association (conflicts with gateway_id)
  subnet_id = aws_subnet.subnet-public-1.id

  # Required: The ID of the routing table to associate with
  route_table_id = aws_route_table.rt-public-1.id
}
