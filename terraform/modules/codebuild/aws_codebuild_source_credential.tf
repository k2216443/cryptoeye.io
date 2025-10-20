# AWS CodeBuild Source Credential - GitHub authentication for CodeBuild
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/codebuild_source_credential

resource "aws_codebuild_source_credential" "github" {
  # Required: Authentication type
  auth_type = "PERSONAL_ACCESS_TOKEN"

  # Required: Source control server type
  server_type = "GITHUB"

  # Required: GitHub personal access token
  token = var.github_token
}
