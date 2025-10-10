resource "aws_ecr_repository" "app" {
  name                 = var.name
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}


