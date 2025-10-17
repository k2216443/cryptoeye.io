
variable "vpc_id" {
  description = "vpc_id"
  type        = string
}

variable "target_id" {
  description = "Target ID"
  type = string
}

variable "subnets" {
  description = "subnets for LB"
  type = list(string)
}