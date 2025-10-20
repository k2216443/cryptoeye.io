# Terraform Variables for EC2 Module
# Documentation: https://developer.hashicorp.com/terraform/language/values/variables

variable "instance_type" {
  description = "Instance Type"
  type        = string
}

variable "disk_size" {
  type    = number
  default = 6
}

variable "private_ip" {
  type = string
}

variable "expose" {
  type    = bool
  default = true
}

variable "account" {
  description = "AWS Account"
  type        = string
  default     = "dev"
}

variable "ssh_key" {
  description = "SSH key for instance"
  default     = "dev.aws_key_pair-2023-05-19"
  type        = string
}

variable "ami" {
  description = "AMI"
  type        = string
}

variable "name" {
  description = "Name"
  type        = string
}

variable "vpc" {
  description = "VPC"
  type        = string
}

variable "subnet" {
  description = "subnet"
  type        = string
}

variable "ingresses" {
  type    = list(any)
  default = []
}

variable "policy" {
  type = string
}
