# AWS VPC Data Source - Fetches existing VPC information
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/vpc

data "aws_vpc" "vpc" {
  # Optional: Filter block to find VPC by tags
  filter {
    # Required: Filter name
    name = "tag:Name"

    # Required: Filter values
    values = [var.vpc]
  }
}

# AWS Subnet Data Source - Fetches existing subnet information
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/subnet

data "aws_subnet" "subnet" {
  # Optional: Filter block to find subnet by tags
  filter {
    # Required: Filter name
    name = "tag:Name"

    # Required: Filter values
    values = [var.subnet]
  }
}
