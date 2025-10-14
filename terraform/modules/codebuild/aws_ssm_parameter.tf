resource "aws_ssm_parameter" "tg_bot_token" {
  name  = "/cryptoeye/telegram_bot_token"
  type  = "SecureString"
  value = var.telegram_bot_token
}

resource "aws_ssm_parameter" "tg_chat_id" {
  name  = "/cryptoeye/telegram_chat_id"
  type  = "String"
  value = "194219638"
  tags = {
    app = "cryptoeye"
  }
}

