resource "aws_codebuild_webhook" "any_branch" {
  project_name = aws_codebuild_project.build.name
  build_type   = "BUILD"
  filter_group {
    filter {
      type    = "EVENT"
      pattern = "PUSH"
    }
    filter {
      type    = "HEAD_REF"
      pattern = "main"
    }
  }
}