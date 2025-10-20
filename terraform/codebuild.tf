# Module: CodeBuild project for CI/CD pipeline with ECR repository

module "codebuild" {
  source = "./modules/codebuild"

  # Required: Docker image for the build environment
  image              = "aws/codebuild/amazonlinux-aarch64-standard:3.0"

  # Required: Compute type for the build environment
  type               = "ARM_CONTAINER"

  # Required: Name for the CodeBuild project
  name               = "chaineye"

  # Required: GitHub token for repository access
  github_token       = var.github_token

  # Required: Telegram bot token for notifications
  telegram_bot_token = var.telegram_bot_token

  # Required: Etherscan API key for blockchain integration
  ETHERSCAN_API_KEY  = var.ETHERSCAN_API_KEY
}

# Output: ARN of the ECR repository created by the module
output "ecr_arn" {
  value = module.codebuild.ecr_repository_arn
}