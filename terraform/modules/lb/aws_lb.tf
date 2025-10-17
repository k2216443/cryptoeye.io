resource "aws_lb" "chaineye" {
  name               = "chaineye"
  load_balancer_type = "application"
  internal           = false
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.subnets
}