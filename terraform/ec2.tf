# Module: EC2 instance for running the application with security groups and IAM roles

module "ec2" {
  source = "./modules/ec2"

  # Required: Amazon Machine Image ID (Amazon Linux 2023 kernel-6.1 AMI)
  ami = "ami-07b2b18045edffe90"

  # Required: EC2 instance type determining compute and memory capacity
  instance_type = "t4g.nano"

  # Required: VPC name tag where the instance will be deployed
  vpc = module.network.vpc_name

  # Required: Subnet name tag within the VPC for instance placement
  subnet = module.network.subnet-public-0-name

  # Required: Name tag for the EC2 instance
  name = "chaineye-0"

  # Required: Whether the instance should have a public IP address
  expose = true

  # Required: SSH key pair name for instance access
  ssh_key = aws_key_pair.chaineye.key_name

  # Required: List of ingress rules defining allowed inbound traffic
  ingresses = [
    {
      "proto" : "tcp",
      "port" : 22,
      "cidr_blocks" : [
        "34.116.218.156/32",
        "3.67.48.151/32"
      ]
    },
    {
      "proto" : "tcp",
      "port" : 8080,
      "cidr_blocks" : [
        "0.0.0.0/0"
      ]
    }
  ]

  # Optional: Root volume size in GB
  disk_size  = 10

  # Optional: Private IP address within the subnet
  private_ip = "172.16.0.10"

  # Optional: IAM policy document for instance role permissions
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF
}

# Output: Public IP address of the EC2 instance
output "public_ip" {
  value = module.ec2.public_ip
}

# Output: EC2 instance ID
output "instance-id" {
  value = module.ec2.instance-id
}