
variable "name" {
  description = "Name"
  type        = string
}

variable "cidr" {
  description = "CIDR"
  type        = string
  default     = "192.168.0.0/24"
}

variable "region" {
  description = "EKS zone"
  type        = string
  default     = "us-west-2"
}