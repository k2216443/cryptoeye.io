resource "aws_codebuild_project" "build" {
  name          = "${var.name}-build"
  service_role  = aws_iam_role.codebuild.arn
  build_timeout = 30

  artifacts { type = "NO_ARTIFACTS" }

  environment {
    compute_type = "BUILD_GENERAL1_SMALL"

    # Ubuntu 22.04 + Docker
    image = "aws/codebuild/standard:7.0"
    type  = "LINUX_CONTAINER"

    # needed for docker build
    privileged_mode             = true
    image_pull_credentials_type = "CODEBUILD"

    environment_variable {
      name  = "AWS_REGION"
      value = var.aws_region
    }

    environment_variable {
      name  = "IMAGE_REPO_URI"
      value = aws_ecr_repository.app.repository_url
    }
  }

  logs_config {
    cloudwatch_logs {
      status = "ENABLED"
    }
  }

  # Build on any branch via GitHub webhook
  source {
    type                = "GITHUB"
    location            = "https://github.com/${var.github_owner}/${var.github_repo}.git"
    report_build_status = true
    git_clone_depth     = 1
  }
}