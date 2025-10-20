# AWS Elastic IP - Static public IPv4 address
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/eip

resource "aws_eip" "eip" {
  # Optional: Number of resources to create (conditional)
  count = var.expose ? 1 : 0

  # Optional: EC2 instance ID to associate with
  instance = aws_instance.instance.id

  # Optional: Resource tags
  tags = {
    Name = var.name
  }
}
