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

# data "aws_iam_policy_document" "codebuild_policy" {
#   statement {
#     sid       = "ECRAuth"
#     effect    = "Allow"
#     actions   = ["ecr:GetAuthorizationToken"]
#     resources = ["*"]
#   }
#     statement {
#     effect = "Allow"
#     actions = ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParameterHistory"]
#     resources = [
#       aws_ssm_parameter.tg_bot_token.arn,
#       aws_ssm_parameter.tg_chat_id.arn
#     ]
#   }
#   statement {
#     sid    = "LambdaUpdate"
#     effect = "Allow"
#     actions = [
#       "lambda:UpdateFunctionCode",
#       "lambda:GetFunctionConfiguration"
#     ]
#     resources = [aws_lambda_function.fn.arn]
#   }
#   statement {
#     sid    = "ECRPush"
#     effect = "Allow"
#     actions = [
#       "ecr:BatchCheckLayerAvailability",
#       "ecr:CompleteLayerUpload",
#       "ecr:InitiateLayerUpload",
#       "ecr:PutImage",
#       "ecr:UploadLayerPart",
#       "ecr:BatchGetImage",
#       "ecr:DescribeRepositories",
#       "ecr:GetDownloadUrlForLayer"
#     ]
#     resources = [
#       "${aws_ecr_repository.app.arn}",
#       "${aws_ecr_repository.python.arn}",
#     ]
#   }
#   statement {
#     sid    = "Logs"
#     effect = "Allow"
#     actions = [
#       "logs:CreateLogGroup",
#       "logs:CreateLogStream",
#       "logs:PutLogEvents"
#     ]
#     resources = ["*"]
#   }
#   statement {
#     sid       = "STSRead"
#     effect    = "Allow"
#     actions   = ["sts:GetCallerIdentity"]
#     resources = ["*"]
#   }
# }

resource "aws_iam_policy" "lambda_ecr_pull" {
  name   = "${var.name}-ecr-pull"
  policy = data.aws_iam_policy_document.lambda_ecr_pull.json
}
