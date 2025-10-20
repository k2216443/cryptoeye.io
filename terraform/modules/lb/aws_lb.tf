# AWS Application Load Balancer - Layer 7 load balancer for HTTP/HTTPS traffic
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb

resource "aws_lb" "chaineye" {
  # Optional: Load balancer name
  name = "chaineye"

  # Optional: Load balancer type (application, network, or gateway)
  load_balancer_type = "application"

  # Optional: Whether the load balancer is internal or internet-facing
  internal = false

  # Optional: List of security group IDs
  security_groups = [aws_security_group.alb.id]

  # Required: List of subnet IDs
  subnets = var.subnets
}
