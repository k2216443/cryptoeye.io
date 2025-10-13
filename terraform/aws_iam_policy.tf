resource "aws_iam_policy" "codebuild" {
  name   = "${var.name}-codebuild-policy"
  policy = data.aws_iam_policy_document.codebuild_policy.json
}

data "aws_iam_policy_document" "codebuild_policy" {
  statement {
    sid       = "ECRAuth"
    effect    = "Allow"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }
    statement {
    effect = "Allow"
    actions = ["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParameterHistory"]
    resources = [
      aws_ssm_parameter.tg_bot_token.arn,
      aws_ssm_parameter.tg_chat_id.arn
    ]
  }
  statement {
    sid    = "LambdaUpdate"
    effect = "Allow"
    actions = [
      "lambda:UpdateFunctionCode",
      "lambda:GetFunctionConfiguration"
    ]
    resources = [aws_lambda_function.fn.arn]
  }
  statement {
    sid    = "ECRPush"
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:CompleteLayerUpload",
      "ecr:InitiateLayerUpload",
      "ecr:PutImage",
      "ecr:UploadLayerPart",
      "ecr:BatchGetImage",
      "ecr:DescribeRepositories",
      "ecr:GetDownloadUrlForLayer"
    ]
    resources = [
      "${aws_ecr_repository.app.arn}",
      "${aws_ecr_repository.python.arn}",
    ]
  }
  statement {
    sid    = "Logs"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["*"]
  }
  statement {
    sid       = "STSRead"
    effect    = "Allow"
    actions   = ["sts:GetCallerIdentity"]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "lambda_ecr_pull" {
  name   = "${var.name}-ecr-pull"
  policy = data.aws_iam_policy_document.lambda_ecr_pull.json
}
