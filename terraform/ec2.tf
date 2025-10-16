module "ec2" {
  source = "./modules/ec2"

  # (Required) Amazon machine Instance 
  # Amazon Linux 2023 kernel-6.1 AMI
  ami = "ami-07b2b18045edffe90"

  # The instance size/type, determining the compute and memory capacity.
  instance_type = "t4g.nano"

  # The name of the SSH key to be used for the instance. 
  # This key was created or imported into AWS on 2023-07-14 for the 'wayside.sandbox' environment.
  # ssh_key = "wayside.sandbox-2023-07-14"

  # The identifier or name tag of the Virtual Private Cloud (VPC) where the instance will be deployed.
  # The name suggests this is a sandbox or non-production environment.
  vpc = module.network.vpc_name

  # The identifier or name tag of the subnet within the VPC where the instance will be deployed.
  # This is the first subnet within the 'sandbox' VPC.
  subnet = module.network.subnet-public-0-name

  # The descriptive name for the instance, indicating its purpose or application.
  # In this case, the instance is likely running the Jenkins continuous integration server.
  name = "cryptoeye-0"

  # A boolean flag that determines whether the instance should be publicly accessible 
  # (e.g., have a public IP or be placed in a public subnet). 
  # A value of 'true' suggests it will be exposed to the public internet.
  expose = true

  ssh_key = aws_key_pair.cryptoeye.key_name

  # A list of ingress rules that define what kind of network traffic is allowed to reach the instance.
  # This configuration allows TCP traffic on ports 443 (typically HTTPS) and 22 (SSH).
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

  disk_size  = 10
  private_ip = "172.16.0.10"

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

output "public_ip" {
  value = module.ec2.public_ip
}

output "instance-id" {
  value = module.ec2.instance-id
}