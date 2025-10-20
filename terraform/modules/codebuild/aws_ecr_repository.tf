# AWS ECR Repository - Elastic Container Registry for Docker images
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/ecr_repository

resource "aws_ecr_repository" "app" {
  # Required: Name of the repository
  name = var.name

  # Optional: Tag mutability setting (MUTABLE or IMMUTABLE)
  image_tag_mutability = "IMMUTABLE"

  # Optional: Image scanning configuration block
  image_scanning_configuration {
    # Required: Whether images are scanned after being pushed
    scan_on_push = false
  }
}

resource "aws_ecr_repository" "python" {
  # Required: Name of the repository
  name = "python"

  # Optional: Tag mutability setting (MUTABLE or IMMUTABLE)
  image_tag_mutability = "IMMUTABLE"

  # Optional: Image scanning configuration block
  image_scanning_configuration {
    # Required: Whether images are scanned after being pushed
    scan_on_push = false
  }
}

resource "aws_ecr_repository" "static_site" {
  # Required: Name of the repository
  name = "${var.name}-site"

  # Optional: Tag mutability setting (MUTABLE or IMMUTABLE)
  image_tag_mutability = "IMMUTABLE"

  # Optional: Image scanning configuration block
  image_scanning_configuration {
    # Required: Whether images are scanned after being pushed
    scan_on_push = false
  }
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "ecr_repository_arn" {
  value = aws_ecr_repository.app.arn
}

output "ecr_static_site_repository_url" {
  value = aws_ecr_repository.static_site.repository_url
}

output "ecr_static_site_repository_arn" {
  value = aws_ecr_repository.static_site.arn
}
