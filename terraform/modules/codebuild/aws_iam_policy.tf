# AWS IAM Policy - Permissions policy for CodeBuild service role
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy

resource "aws_iam_policy" "codebuild" {
  # Required: Policy name
  name = "${var.name}-codebuild-policy"

  # Required: Policy document in JSON format
  policy = jsonencode(
    {
      Version = "2012-10-17"
      Statement = [
        {
          # Optional: Statement ID
          Sid = "ECRAuth"

          # Optional: Effect (Allow or Deny)
          Effect = "Allow"

          # Optional: List of actions
          Action = "ecr:GetAuthorizationToken"

          # Optional: Resources this statement applies to
          Resource = "*"
        },
        {
          # Optional: Effect (Allow or Deny)
          Effect = "Allow"

          # Optional: List of actions for SSM Parameter Store
          Action = [
            "ssm:GetParameters",
            "ssm:GetParameterHistory",
            "ssm:GetParameter",
          ]

          # Optional: Specific SSM parameter ARNs
          Resource = [
            "arn:aws:ssm:us-west-2:292875404443:parameter/cryptoeye/telegram_chat_id",
            "arn:aws:ssm:us-west-2:292875404443:parameter/cryptoeye/telegram_bot_token",
          ]
        },
        {
          # Optional: Statement ID
          Sid = "LambdaUpdate"

          # Optional: Effect (Allow or Deny)
          Effect = "Allow"

          # Optional: List of actions for Lambda function updates
          Action = [
            "lambda:UpdateFunctionCode",
            "lambda:GetFunctionConfiguration",
          ]

          # Optional: Lambda function ARN
          Resource = "arn:aws:lambda:us-west-2:292875404443:function:cryptoeye"
        },
        {
          # Optional: Statement ID
          Sid = "ECRPush"

          # Optional: Effect (Allow or Deny)
          Effect = "Allow"

          # Optional: List of actions for ECR image operations
          Action = [
            "ecr:UploadLayerPart",
            "ecr:PutImage",
            "ecr:InitiateLayerUpload",
            "ecr:GetDownloadUrlForLayer",
            "ecr:DescribeRepositories",
            "ecr:CompleteLayerUpload",
            "ecr:BatchGetImage",
            "ecr:BatchCheckLayerAvailability",
          ]

          # Optional: ECR repository ARNs
          Resource = [
            "arn:aws:ecr:us-west-2:292875404443:repository/python",
            "arn:aws:ecr:us-west-2:292875404443:repository/cryptoeye",
            "arn:aws:ecr:us-west-2:292875404443:repository/chaineye-site",
          ]
        },
        {
          # Optional: Statement ID
          Sid = "Logs"

          # Optional: Effect (Allow or Deny)
          Effect = "Allow"

          # Optional: List of actions for CloudWatch Logs
          Action = [
            "logs:PutLogEvents",
            "logs:CreateLogStream",
            "logs:CreateLogGroup",
          ]

          # Optional: Resources this statement applies to
          Resource = "*"
        },
        {
          # Optional: Statement ID
          Sid = "STSRead"

          # Optional: Effect (Allow or Deny)
          Effect = "Allow"

          # Optional: Action for getting caller identity
          Action = "sts:GetCallerIdentity"

          # Optional: Resources this statement applies to
          Resource = "*"
        },
      ]
    }
  )
}
