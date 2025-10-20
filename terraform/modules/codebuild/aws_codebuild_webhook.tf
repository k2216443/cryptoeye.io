# AWS CodeBuild Webhook - Triggers builds from GitHub events
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/codebuild_webhook

resource "aws_codebuild_webhook" "any_branch" {
  # Required: CodeBuild project name
  project_name = aws_codebuild_project.build.name

  # Optional: Type of build to trigger
  build_type = "BUILD"

  # Optional: Filter groups for webhook triggers
  filter_group {
    # Optional: Individual filter within the group
    filter {
      # Required: Filter type
      type = "EVENT"

      # Required: Pattern to match
      pattern = "PUSH"
    }

    filter {
      # Required: Filter type
      type = "HEAD_REF"

      # Required: Branch pattern to match
      pattern = "main"
    }
  }
}
