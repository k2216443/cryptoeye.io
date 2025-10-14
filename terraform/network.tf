module "network" {
  source = "./modules/network"

  # (Optional) Region to deploy network
  region = "us-west-2"

  # (Required) Network Name
  name = "cryptoeye"

  # (Optional) Network Cidr
  cidr = "192.168.0.0/24"
}

output "subnet" {
  value = module.network.subnet
}

output "vpc_id" {
  value = module.network.vpc_id
}

output "subnet_name" {
  value = module.network.subnet_name
}

output "vpc_name" {
  value = module.network.vpc_name
}