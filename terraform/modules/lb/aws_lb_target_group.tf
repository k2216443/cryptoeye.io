# AWS Load Balancer Target Group - Defines targets for load balancer routing
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_target_group

resource "aws_lb_target_group" "backend" {
  # Optional: Target group name
  name = "tg-backend-8080"

  # Required: Port for routing traffic to targets
  port = 8080

  # Required: Protocol for routing traffic (HTTP, HTTPS, TCP, etc.)
  protocol = "HTTP"

  # Required: VPC ID where targets are located
  vpc_id = var.vpc_id

  # Optional: Health check configuration
  health_check {
    # Optional: Health check path
    path = "/health"

    # Optional: Health check protocol
    protocol = "HTTP"

    # Optional: Number of consecutive successful checks before marking healthy
    healthy_threshold = 2

    # Optional: Number of consecutive failed checks before marking unhealthy
    unhealthy_threshold = 2

    # Optional: Health check timeout in seconds
    timeout = 5

    # Optional: Health check interval in seconds
    interval = 15
  }
}
