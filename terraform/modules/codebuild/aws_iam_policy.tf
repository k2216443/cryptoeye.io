resource "aws_iam_policy" "codebuild" {
  name = "${var.name}-codebuild-policy"
  policy = jsonencode(
    {
      Statement = [
        {
          Action   = "ecr:GetAuthorizationToken"
          Effect   = "Allow"
          Resource = "*"
          Sid      = "ECRAuth"
        },
        {
          Action = [
            "ssm:GetParameters",
            "ssm:GetParameterHistory",
            "ssm:GetParameter",
          ]
          Effect = "Allow"
          Resource = [
            "arn:aws:ssm:us-west-2:292875404443:parameter/cryptoeye/telegram_chat_id",
            "arn:aws:ssm:us-west-2:292875404443:parameter/cryptoeye/telegram_bot_token",
          ]
        },
        {
          Action = [
            "lambda:UpdateFunctionCode",
            "lambda:GetFunctionConfiguration",
          ]
          Effect   = "Allow"
          Resource = "arn:aws:lambda:us-west-2:292875404443:function:cryptoeye"
          Sid      = "LambdaUpdate"
        },
        {
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
          Effect = "Allow"
          Resource = [
            "arn:aws:ecr:us-west-2:292875404443:repository/python",
            "arn:aws:ecr:us-west-2:292875404443:repository/cryptoeye",
          ]
          Sid = "ECRPush"
        },
        {
          Action = [
            "logs:PutLogEvents",
            "logs:CreateLogStream",
            "logs:CreateLogGroup",
          ]
          Effect   = "Allow"
          Resource = "*"
          Sid      = "Logs"
        },
        {
          Action   = "sts:GetCallerIdentity"
          Effect   = "Allow"
          Resource = "*"
          Sid      = "STSRead"
        },
      ]
      Version = "2012-10-17"
    }
  )
}

