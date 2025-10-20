# AWS SSM Parameter - Systems Manager Parameter Store for secure configuration
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ssm_parameter

resource "aws_ssm_parameter" "tg_bot_token" {
  # Required: Parameter name
  name = "/cryptoeye/telegram_bot_token"

  # Required: Parameter type (String, StringList, or SecureString)
  type = "SecureString"

  # Required: Parameter value
  value = var.telegram_bot_token
}

resource "aws_ssm_parameter" "tg_chat_id" {
  # Required: Parameter name
  name = "/cryptoeye/telegram_chat_id"

  # Required: Parameter type (String, StringList, or SecureString)
  type = "String"

  # Required: Parameter value
  value = "194219638"

  # Optional: Resource tags
  tags = {
    app = "cryptoeye"
  }
}
