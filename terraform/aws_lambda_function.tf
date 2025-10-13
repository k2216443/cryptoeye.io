resource "aws_lambda_function" "fn" {
  function_name = var.name
  role          = aws_iam_role.lambda_role.arn

  package_type = "Image"
  image_uri    = var.image_uri

  architectures = ["x86_64"]
  memory_size   = "64"
  timeout       = "10"

  depends_on = [aws_iam_role.lambda_role]

  lifecycle {
    ignore_changes = [image_uri]
  }
}
