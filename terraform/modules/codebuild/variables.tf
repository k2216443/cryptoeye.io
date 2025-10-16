variable "name" {
  type    = string
  default = "cryptoeye"
}

variable "github_token" {
  type = string
}

variable "aws_region" {
  type    = string
  default = "us-west-2"
}

variable "github_owner" {
  type    = string
  default = "k2216443"
}

variable "github_repo" {
  type    = string
  default = "cryptoeye.io"
}

variable "ETHERSCAN_API_KEY" {
  type = string
}

variable "telegram_bot_token" {
  type = string
}

variable "image" {
  type    = string
  default = "aws/codebuild/standard:7.0"
}

variable "type" {
  type    = string
  default = "LINUX_CONTAINER"
}