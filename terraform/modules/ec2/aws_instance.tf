# AWS EC2 Instance - Virtual server in AWS
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/instance

resource "aws_instance" "instance" {
  # Required: AMI ID to use for the instance
  ami = var.ami

  # Required: Instance type (e.g., t2.micro, m5.large)
  instance_type = var.instance_type

  # Optional: SSH key name for instance access
  key_name = var.ssh_key

  # Optional: Enable detailed CloudWatch monitoring
  monitoring = true

  # Optional: Enable EBS optimization for supported instance types
  ebs_optimized = true

  # Optional: Associate public IP address with instance
  associate_public_ip_address = var.expose

  # Required: Subnet ID where instance will be launched
  subnet_id = data.aws_subnet.subnet.id

  # Optional: List of security group IDs
  vpc_security_group_ids = [
    aws_security_group.sg.id
  ]

  # Optional: Private IP address for the instance
  private_ip = var.private_ip

  # Optional: Root block device configuration
  root_block_device {
    # Optional: Delete root volume on instance termination
    delete_on_termination = true

    # Optional: Enable EBS encryption
    encrypted = false

    # Optional: Tags for the root volume
    tags = {
      "Name" : "${var.name}"
    }

    # Optional: Root volume size in GiB
    volume_size = var.disk_size

    # Optional: Volume type (gp2, gp3, io1, etc.)
    volume_type = "gp2"
  }

  # Optional: IAM instance profile name
  iam_instance_profile = aws_iam_instance_profile.ecsInstanceProfile.name

  # Optional: Resource tags
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
