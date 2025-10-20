# Module: Network infrastructure including VPC, subnets, and routing

module "network" {
  source = "./modules/network"

  # Optional: AWS region to deploy network resources
  region = "us-west-2"

  # Required: Name tag for the network resources
  name = "cryptoeye"

  # Optional: CIDR block for the VPC
  cidr = "172.16.0.0/16"
}

# Output: First public subnet ID
output "subnet-public-0-id" {
  value = module.network.subnet-public-0-id
}

# Output: First public subnet name tag
output "subnet-public-0-name" {
  value = module.network.subnet-public-0-name
}

# Output: Second public subnet ID
output "subnet-public-1-id" {
  value = module.network.subnet-public-1-id
}

# Output: Second public subnet name tag
output "subnet-public-1-name" {
  value = module.network.subnet-public-1-name
}

# Output: VPC ID
output "vpc_id" {
  value = module.network.vpc_id
}

# Output: VPC name tag
output "vpc_name" {
  value = module.network.vpc_name
}
