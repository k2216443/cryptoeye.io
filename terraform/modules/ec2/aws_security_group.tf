# ======================================================================================================= #
# VPN environment Security Groups                                                                         #
# ======================================================================================================= #
# Define an AWS Security Group for controlling access to and from instances within a VPC
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group
resource "aws_security_group" "sg" {
  # Name of the security group, should be unique within the VPC
  name = var.name

  # ID of the VPC where the security group is created
  vpc_id = data.aws_vpc.vpc.id

  # Dynamic ingress rules based on provided variables
  dynamic "ingress" {
    for_each = var.ingresses
    content {
      # CIDR blocks from which inbound traffic is allowed for dynamic rules
      cidr_blocks = ingress.value["cidr_blocks"]
      # Description for the dynamic ingress rule
      description = ""
      # The starting port for traffic for dynamic rules
      from_port = ingress.value["port"]
      # The CIDR blocks for IPv6 for dynamic rules (empty in this case)
      ipv6_cidr_blocks = []
      # AWS Prefix List IDs for dynamic rules (not used here)
      prefix_list_ids = []
      # The protocol for dynamic rules
      protocol = ingress.value["proto"]
      # A list of security group IDs to allow access for dynamic rules (not used here)
      security_groups = []
      # Whether the rule applies to the security group itself for dynamic rules (not used here)
      self = false
      # The ending port for traffic for dynamic rules
      to_port = ingress.value["port"]
    }
  }

  # Egress rule allowing all outbound traffic to any IP address
  # See: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/security_group#egress
  egress {
    # The starting port for outbound traffic (0 for all ports)
    from_port = 0
    # The ending port for outbound traffic (0 for all ports)
    to_port = 0
    # The protocol (using -1 for all protocols)
    protocol = "-1"
    # The CIDR blocks to which outbound traffic is allowed
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Tags assigned to the security group
  tags = {
    Name = var.name
  }
}
