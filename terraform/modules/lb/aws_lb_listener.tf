# AWS Load Balancer Listener - Defines how load balancer listens for traffic
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_listener

resource "aws_lb_listener" "https" {
  # Required: ARN of the load balancer
  load_balancer_arn = aws_lb.chaineye.arn

  # Required: Port on which the load balancer listens
  port = 443

  # Required: Protocol for connections (HTTP, HTTPS, TCP, etc.)
  protocol = "HTTPS"

  # Optional: SSL/TLS security policy (for HTTPS/TLS listeners)
  ssl_policy = "ELBSecurityPolicy-2016-08"

  # Optional: ARN of the SSL certificate (required for HTTPS)
  certificate_arn = aws_acm_certificate.chaineye.arn

  # Required: Default action when request matches no rules
  default_action {
    # Required: Type of action (forward, redirect, fixed-response, etc.)
    type = "forward"

    # Optional: ARN of target group to forward to
    target_group_arn = aws_lb_target_group.backend.arn
  }
}

resource "aws_lb_listener" "http_redirect" {
  # Required: ARN of the load balancer
  load_balancer_arn = aws_lb.chaineye.arn

  # Required: Port on which the load balancer listens
  port = 80

  # Required: Protocol for connections
  protocol = "HTTP"

  # Required: Default action to redirect HTTP to HTTPS
  default_action {
    # Required: Type of action
    type = "redirect"

    # Optional: Redirect configuration block
    redirect {
      # Required: Port to redirect to
      port = "443"

      # Required: Protocol to redirect to
      protocol = "HTTPS"

      # Required: HTTP status code for redirect
      status_code = "HTTP_301"
    }
  }
}
