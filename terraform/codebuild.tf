module "codebuild" {
  source = "./modules/codebuild"

  image = "aws/codebuild/amazonlinux-aarch64-standard:3.0"
  type = "ARM_CONTAINER"
  github_token = var.github_token
  telegram_bot_token = var.telegram_bot_token
  ETHERSCAN_API_KEY = var.ETHERSCAN_API_KEY
}
