resource "aws_lb_target_group" "backend" {
  name     = "tg-backend-8080"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = module.network.vpc_id
  health_check {
    path                = "/health"
    protocol            = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 15
  }
}