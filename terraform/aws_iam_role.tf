resource "aws_iam_role" "codebuild" {
  name               = "${var.name}-codebuild-role"
  assume_role_policy = data.aws_iam_policy_document.codebuild_assume.json
}

data "aws_iam_policy_document" "codebuild_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]
    principals { 
        type = "Service"
        identifiers = ["codebuild.amazonaws.com"] 
    }
  }
}