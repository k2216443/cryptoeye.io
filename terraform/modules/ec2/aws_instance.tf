# Define an AWS EC2 instance
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance
resource "aws_instance" "instance" {
  # AMI ID to use for the instance
  # See: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#ami
  ami = var.ami

  # The instance type (e.g., t2.micro, m5.large)
  # See: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#instance_type
  instance_type = var.instance_type

  # The key name of the SSH key to attach for the instance
  # See: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#key_name
  key_name   = var.ssh_key
  monitoring = true

  # Enable EBS optimization for supported instance types
  # See: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#ebs_optimized
  ebs_optimized = true

  # Associate a network interface with the instance
  # See: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#network_interface
  # network_interface {
  #   # ID of the network interface to attach to the instance
  #   network_interface_id = aws_network_interface.nt.id
  #   # The index of the network interface (0 for primary interface)
  #   device_index = 0
  # }

  # Whether to associate a public IP address with the instance (false for private instances)
  # See: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#associate_public_ip_address
  associate_public_ip_address = var.expose
  subnet_id                   = data.aws_subnet.subnet.id
  vpc_security_group_ids = [
    aws_security_group.sg.id
  ]
  private_ip = var.private_ip

  # Configuration for the root block device
  # See: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#root_block_device
  root_block_device {
    # Whether to delete the root block device when the instance is terminated
    delete_on_termination = true
    # Whether the root block device should be encrypted
    encrypted = false
    # Tags for the root block device
    tags = {
      "Name" : "${var.name}"
    }
    # Size of the root volume (in GiB)
    volume_size = var.disk_size
    # Type of volume (gp2 for General Purpose SSD, for example)
    volume_type = "gp2"
  }

  iam_instance_profile = aws_iam_instance_profile.ecsInstanceProfile.name
  # Tags assigned to the instance
  # See: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance#tags
  tags = {
    "Name" : "${var.name}",
    "Module" : "ec2"
  }
}

output "private_ip" {
  value = aws_instance.instance.private_ip
}

output "public_ip" {
  value = aws_instance.instance.public_ip
}

output "instance-id" {
  value = aws_instance.instance.id
}