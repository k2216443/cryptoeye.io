# AWS CodeBuild Project - Continuous integration and build service
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/codebuild_project

resource "aws_codebuild_project" "build" {
  # Required: Project name
  name = "${var.name}-build"

  # Required: IAM role ARN for CodeBuild service
  service_role = aws_iam_role.codebuild.arn

  # Optional: Build timeout in minutes (default: 60)
  build_timeout = 30

  # Required: Artifact configuration
  artifacts {
    # Required: Artifact type
    type = "NO_ARTIFACTS"
  }

  # Required: Build environment configuration
  environment {
    # Required: Compute type for build environment
    compute_type = "BUILD_GENERAL1_SMALL"

    # Required: Docker image for build environment (Ubuntu 22.04 + Docker)
    image = var.image

    # Required: Environment type
    type = var.type

    # Optional: Enable Docker daemon (required for docker build)
    privileged_mode = true

    # Optional: Credentials type for pulling images
    image_pull_credentials_type = "CODEBUILD"

    # Optional: Environment variables
    environment_variable {
      # Required: Variable name
      name = "AWS_REGION"

      # Required: Variable value
      value = var.aws_region
    }

    environment_variable {
      # Required: Variable name
      name = "IMAGE_REPO_URI"

      # Required: Variable value
      value = aws_ecr_repository.app.repository_url
    }

    environment_variable {
      # Required: Variable name
      name = "STATIC_SITE_REPO_URI"

      # Required: Variable value
      value = aws_ecr_repository.static_site.repository_url
    }
  }

  # Optional: CloudWatch Logs configuration
  logs_config {
    cloudwatch_logs {
      # Optional: CloudWatch Logs status
      status = "ENABLED"
    }
  }

  # Required: Source code location and configuration
  source {
    # Required: Source type
    type = "GITHUB"

    # Required: Repository location URL
    location = "https://github.com/${var.github_owner}/${var.github_repo}.git"

    # Optional: Report build status to source provider
    report_build_status = true

    # Optional: Git clone depth (0 for full history)
    git_clone_depth = 1
  }
}
