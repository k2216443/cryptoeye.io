module "network" {
  source = "./modules/network"

  # (Optional) Region to deploy network
  region = "us-west-2"

  # (Required) Network Name
  name = "cryptoeye"

  # (Optional) Network Cidr
  cidr = "172.16.0.0/16"
}

output "subnet-public-0-id" {
  value = module.network.subnet-public-0-id
}
output "subnet-public-0-name" {
  value = module.network.subnet-public-0-name
}

output "subnet-public-1-id" {
  value = module.network.subnet-public-1-id
}
output "subnet-public-1-name" {
  value = module.network.subnet-public-1-name
}

output "vpc_id" {
  value = module.network.vpc_id
}

output "vpc_name" {
  value = module.network.vpc_name
}
