# AWS Security Group - Virtual firewall for EC2 instances
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group

resource "aws_security_group" "sg" {
  # Optional: Security group name (must be unique within VPC)
  name = var.name

  # Required: VPC ID where security group will be created
  vpc_id = data.aws_vpc.vpc.id

  # Optional: Dynamic ingress rules based on input variables
  dynamic "ingress" {
    for_each = var.ingresses
    content {
      # Optional: List of CIDR blocks for inbound traffic
      cidr_blocks = ingress.value["cidr_blocks"]

      # Optional: Rule description
      description = ""

      # Required: Start of port range
      from_port = ingress.value["port"]

      # Optional: List of IPv6 CIDR blocks
      ipv6_cidr_blocks = []

      # Optional: List of AWS Prefix List IDs
      prefix_list_ids = []

      # Required: Protocol (-1 for all, tcp, udp, icmp)
      protocol = ingress.value["proto"]

      # Optional: List of security group IDs to allow access
      security_groups = []

      # Optional: Allow rule to reference itself
      self = false

      # Required: End of port range
      to_port = ingress.value["port"]
    }
  }

  # Optional: Egress rule for outbound traffic
  egress {
    # Required: Start of port range (0 for all)
    from_port = 0

    # Required: End of port range (0 for all)
    to_port = 0

    # Required: Protocol (-1 for all protocols)
    protocol = "-1"

    # Optional: List of CIDR blocks for outbound traffic
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Optional: Resource tags
  tags = {
    Name = var.name
  }
}
