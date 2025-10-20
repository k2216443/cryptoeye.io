# AWS Security Group - Virtual firewall for ALB inbound/outbound traffic control
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group

resource "aws_security_group" "alb" {
  # Optional: Security group name
  name = "alb-https"

  # Optional: Security group description
  description = "Allow HTTPS in"

  # Required: VPC ID where security group will be created
  vpc_id = var.vpc_id

  # Optional: Ingress rule block for inbound traffic
  ingress {
    # Required: Protocol (-1 for all, tcp, udp, icmp)
    protocol = "tcp"

    # Required: Start of port range
    from_port = 443

    # Required: End of port range
    to_port = 443

    # Optional: List of CIDR blocks
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Optional: Egress rule block for outbound traffic
  egress {
    # Required: Protocol (-1 for all protocols)
    protocol = "-1"

    # Required: Start of port range
    from_port = 0

    # Required: End of port range
    to_port = 0

    # Optional: List of CIDR blocks
    cidr_blocks = ["0.0.0.0/0"]
  }
}
