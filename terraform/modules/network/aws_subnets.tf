# AWS Subnet Resource - Provides a VPC subnet resource for network segmentation
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet

resource "aws_subnet" "subnet-public-0" {
  # Optional: Region where this resource will be managed
  region = var.region

  # Optional: Specify true to indicate that network interfaces created in the specified subnet should be assigned an IPv6 address
  assign_ipv6_address_on_creation = false

  # Required: VPC ID where the subnet is created
  vpc_id = aws_vpc.vpc.id

  # Required: The IPv4 CIDR block for the subnet
  cidr_block = cidrsubnet(var.cidr, 2, 0)

  # Optional: Indicates whether DNS queries made to the Amazon-provided DNS Resolver in this subnet should return synthetic IPv6 addresses for IPv4-only destinations
  enable_dns64 = false

  # Optional: AZ for the subnet
  availability_zone = "${var.region}a"

  # Optional: Specify true to indicate that instances launched into the subnet should be assigned a public IP address
  map_public_ip_on_launch = true

  # Optional: The type of hostnames to assign to instances in the subnet at launch
  private_dns_hostname_type_on_launch = "resource-name"

  # Optional: A map of tags to assign to the resource
  tags = {
    Name   = "${var.name}-public-0"
    Module = "network"
  }
}

# AWS Subnet Resource - Provides a VPC subnet resource for network segmentation
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet

resource "aws_subnet" "subnet-public-1" {
  # Optional: Region where this resource will be managed
  region = var.region

  # Optional: Specify true to indicate that network interfaces created in the specified subnet should be assigned an IPv6 address
  assign_ipv6_address_on_creation = false

  # Required: VPC ID where the subnet is created
  vpc_id = aws_vpc.vpc.id

  # Required: The IPv4 CIDR block for the subnet
  cidr_block = cidrsubnet(var.cidr, 2, 1)

  # Optional: Indicates whether DNS queries made to the Amazon-provided DNS Resolver in this subnet should return synthetic IPv6 addresses for IPv4-only destinations
  enable_dns64 = false

  # Optional: AZ for the subnet
  availability_zone = "${var.region}b"

  # Optional: Specify true to indicate that instances launched into the subnet should be assigned a public IP address
  map_public_ip_on_launch = true

  # Optional: The type of hostnames to assign to instances in the subnet at launch
  private_dns_hostname_type_on_launch = "resource-name"

  # Optional: A map of tags to assign to the resource
  tags = {
    Name   = "${var.name}-public-1"
    Module = "network"
  }
}

# AWS Subnet Resource - Provides a VPC subnet resource for network segmentation
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet

resource "aws_subnet" "subnet-private-0" {
  # Optional: Region where this resource will be managed
  region = var.region

  # Optional: Specify true to indicate that network interfaces created in the specified subnet should be assigned an IPv6 address
  assign_ipv6_address_on_creation = false

  # Required: VPC ID where the subnet is created
  vpc_id = aws_vpc.vpc.id

  # Required: The IPv4 CIDR block for the subnet
  cidr_block = cidrsubnet(var.cidr, 2, 2)

  # Optional: Indicates whether DNS queries made to the Amazon-provided DNS Resolver in this subnet should return synthetic IPv6 addresses for IPv4-only destinations
  enable_dns64 = false

  # Optional: AZ for the subnet
  availability_zone = "${var.region}a"

  # Optional: Specify true to indicate that instances launched into the subnet should be assigned a public IP address
  map_public_ip_on_launch = false

  # Optional: The type of hostnames to assign to instances in the subnet at launch
  private_dns_hostname_type_on_launch = "resource-name"

  # Optional: A map of tags to assign to the resource
  tags = {
    Name   = "${var.name}-private-0"
    Module = "network"
  }
}

# AWS Subnet Resource - Provides a VPC subnet resource for network segmentation
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/subnet

resource "aws_subnet" "subnet-private-1" {
  # Optional: Region where this resource will be managed
  region = var.region

  # Optional: Specify true to indicate that network interfaces created in the specified subnet should be assigned an IPv6 address
  assign_ipv6_address_on_creation = false

  # Required: VPC ID where the subnet is created
  vpc_id = aws_vpc.vpc.id

  # Required: The IPv4 CIDR block for the subnet
  cidr_block = cidrsubnet(var.cidr, 2, 3)

  # Optional: Indicates whether DNS queries made to the Amazon-provided DNS Resolver in this subnet should return synthetic IPv6 addresses for IPv4-only destinations
  enable_dns64 = false

  # Optional: AZ for the subnet
  availability_zone = "${var.region}b"

  # Optional: Specify true to indicate that instances launched into the subnet should be assigned a public IP address
  map_public_ip_on_launch = false

  # Optional: The type of hostnames to assign to instances in the subnet at launch
  private_dns_hostname_type_on_launch = "resource-name"

  # Optional: A map of tags to assign to the resource
  tags = {
    Name   = "${var.name}-private-1"
    Module = "network"
  }
}

output "subnet-public-0-id" {
  value = aws_subnet.subnet-public-0.id
}

output "subnet-public-0-name" {
  value = aws_subnet.subnet-public-0.tags["Name"]
}

output "subnet-public-1-id" {
  value = aws_subnet.subnet-public-1.id
}

output "subnet-public-1-name" {
  value = aws_subnet.subnet-public-1.tags["Name"]
}
