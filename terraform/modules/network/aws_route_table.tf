# AWS Route Table - Provides a resource to create a VPC routing table
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table

resource "aws_route_table" "rt-public-0" {
  # Required: The VPC ID
  vpc_id = aws_vpc.vpc.id

  # Optional: Region where this resource will be managed
  region = var.region

  # Optional: A list of route objects
  route {
    # Required: The CIDR block of the route
    cidr_block = "0.0.0.0/0"

    # Optional: Identifier of a VPC internet gateway or virtual private gateway
    gateway_id = aws_internet_gateway.igw.id
  }

  # Optional: A map of tags to assign to the resource
  tags = {
    "Name"   = "${var.name}-public-0"
    "Module" = "network"
  }
}

# AWS Route Table - Provides a resource to create a VPC routing table
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route_table

resource "aws_route_table" "rt-public-1" {
  # Required: The VPC ID
  vpc_id = aws_vpc.vpc.id

  # Optional: Region where this resource will be managed
  region = var.region

  # Optional: A list of route objects
  route {
    # Required: The CIDR block of the route
    cidr_block = "0.0.0.0/0"

    # Optional: Identifier of a VPC internet gateway or virtual private gateway
    gateway_id = aws_internet_gateway.igw.id
  }

  # Optional: A map of tags to assign to the resource
  tags = {
    "Name"   = "${var.name}-public-1"
    "Module" = "network"
  }
}

output "route-table-public-0-id" {
  value = aws_route_table.rt-public-0.id
}

output "route-table-public-1-id" {
  value = aws_route_table.rt-public-1.id
}

