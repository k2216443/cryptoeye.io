variable "project" {
  description = "Project name, used in resource names"
  type        = string
}

variable "env" {
  description = "Environment, e.g. prod, dev"
  type        = string
}

variable "region" {
  description = "AWS region, e.g. eu-west-1"
  type        = string
}

variable "domain_prefix" {
  description = "Hosted UI domain prefix (must be globally unique per region)"
  type        = string
}

variable "callback_urls" {
  description = "Allowed OAuth2 callback URLs"
  type        = list(string)
}

variable "logout_urls" {
  description = "Allowed OAuth2 logout URLs"
  type        = list(string)
}

variable "google_client_id" {
  description = "Google OAuth client id"
  type        = string
  sensitive   = true
}

variable "google_client_secret" {
  description = "Google OAuth client secret"
  type        = string
  sensitive   = true
}

variable "tags" {
  description = "Resource tags"
  type        = map(string)
  default     = {}
}
