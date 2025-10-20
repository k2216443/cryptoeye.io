# Module: Application Load Balancer with target groups and listeners

module "lb" {
  source = "./modules/lb"

  # Required: EC2 instance ID to register as a target
  target_id = module.ec2.instance-id

  # Required: VPC ID where the load balancer will be created
  vpc_id = module.network.vpc_id

  # Required: List of subnet IDs for load balancer placement (requires at least 2 subnets in different AZs)
  subnets = [module.network.subnet-public-0-id, module.network.subnet-public-1-id]
}