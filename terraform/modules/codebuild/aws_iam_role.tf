# AWS IAM Role - Identity and Access Management role for CodeBuild
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role

resource "aws_iam_role" "codebuild" {
  # Required: Role name
  name = "${var.name}-codebuild-role"

  # Required: Assume role policy document (JSON)
  assume_role_policy = data.aws_iam_policy_document.codebuild_assume.json
}

# AWS IAM Policy Document - Data source for generating IAM policy JSON
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document

data "aws_iam_policy_document" "codebuild_assume" {
  # Optional: Policy statement block
  statement {
    # Optional: Effect (Allow or Deny)
    effect = "Allow"

    # Optional: List of actions
    actions = ["sts:AssumeRole"]

    # Optional: Principal block specifying who can assume the role
    principals {
      # Required: Principal type
      type = "Service"

      # Required: List of principal identifiers
      identifiers = ["codebuild.amazonaws.com"]
    }
  }
}
