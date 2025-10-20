# Terraform Variables for Root Configuration
# Documentation: https://developer.hashicorp.com/terraform/language/values/variables

variable "github_token" {
  # Required: GitHub personal access token for CodeBuild to access repositories
  type = string
}

variable "ETHERSCAN_API_KEY" {
  # Required: API key for Etherscan blockchain explorer integration
  type = string
}

variable "telegram_bot_token" {
  # Required: Token for Telegram bot notifications
  type = string
}

