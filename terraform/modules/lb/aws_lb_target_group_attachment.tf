# AWS Load Balancer Target Group Attachment - Attaches target to target group
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lb_target_group_attachment

resource "aws_lb_target_group_attachment" "backend_instance" {
  # Required: ARN of the target group
  target_group_arn = aws_lb_target_group.backend.arn

  # Required: ID of the target (instance ID, IP address, or Lambda function ARN)
  target_id = var.target_id

  # Optional: Port on which the target receives traffic
  port = 8080
}
