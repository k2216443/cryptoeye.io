
variable "name" {
  description = "Name"
  type        = string
}

variable "cidr" {
  description = "CIDR"
  type        = string
  default     = "172.16.0.0/16"
}

variable "region" {
  description = "EKS zone"
  type        = string
  default     = "us-west-2"
}