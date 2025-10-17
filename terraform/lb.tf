module "lb" {
  source = "./modules/lb"
  target_id = module.ec2.instance-id
  vpc_id = module.network.vpc_id
  subnets = [module.network.subnet-public-0-id, module.network.subnet-public-1-id]
}