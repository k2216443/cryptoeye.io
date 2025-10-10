# variable "project_name" { type = string }
# variable "aws_region"   { 
#     type = string  
#     default = "eu-central-1" 
#     }
# variable "github_owner" { type = string }
# variable "github_repo"  { type = string }
# # PAT needs repo:status, repo, admin:repo_hook (or use public repo)
# variable "github_token" { 
#     type = string
# sensitive = true 
# }
# variable "ecr_repo_name"{ type = string
# default = "walletscan" 
# }

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
  type = string
  default = "k2216443"
}

variable "github_repo" {
  type = string
  default = "cryptoeye.io"
}
