resource "aws_lb" "chaineye" {
  name               = "chaineye"
  load_balancer_type = "application"
  internal           = false
  security_groups    = [aws_security_group.alb.id]
  subnets            = [module.network.subnet-public-0-id, module.network.subnet-public-1-id]
}