# AWS EC2 Terraform Module
This module provides resources for deploying an EC2 instance in AWS, with the option to assign an Elastic IP (EIP) and configure network interfaces and security groups.

# Features

* Optional EIP attachment.
* Preconfigured security group with custom ingress rules.
* Network Interface creation and attachment to the instance.
* Data sources to fetch VPC and Subnet information based on tags.
* Outputs the private IP of the created instance.

# Usage

```
module "aws_ec2_instance" {
  source = "../../../modules/instance"

  # Check AMI: https://alt.fedoraproject.org/cloud/
  # The Amazon Machine Image ID representing the base OS for the instance.
  ami = "ami-08ac3f0aafa051220"

  # The instance size/type, determining the compute and memory capacity.
  instance_type = "t3.medium"

  # The name of the SSH key to be used for the instance. 
  # This key was created or imported into AWS on 2023-07-14 for the 'wayside.sandbox' environment.
  ssh_key = "wayside.sandbox-2023-07-14"

  # The identifier or name tag of the Virtual Private Cloud (VPC) where the instance will be deployed.
  # The name suggests this is a sandbox or non-production environment.
  vpc = "sandbox"

  # The identifier or name tag of the subnet within the VPC where the instance will be deployed.
  # This is the first subnet within the 'sandbox' VPC.
  subnet = "sandbox-1"

  # The descriptive name for the instance, indicating its purpose or application.
  # In this case, the instance is likely running the Jenkins continuous integration server.
  name = "jenkins"

  # A boolean flag that determines whether the instance should be publicly accessible 
  # (e.g., have a public IP or be placed in a public subnet). 
  # A value of 'true' suggests it will be exposed to the public internet.
  expose = true
  
  # A list of ingress rules that define what kind of network traffic is allowed to reach the instance.
  # This configuration allows TCP traffic on ports 443 (typically HTTPS) and 22 (SSH).
  ingresses = [
    {
      "proto" : "tcp",
      "port" : 443
    },
    {
      "proto" : "tcp",
      "port" : 22
    }
  ]
}
```