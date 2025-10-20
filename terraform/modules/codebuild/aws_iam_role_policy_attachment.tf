# AWS IAM Role Policy Attachment - Attaches IAM policy to IAM role
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment

resource "aws_iam_role_policy_attachment" "codebuild_attach" {
  # Required: IAM role name to attach policy to
  role = aws_iam_role.codebuild.name

  # Required: ARN of the policy to attach
  policy_arn = aws_iam_policy.codebuild.arn
}
