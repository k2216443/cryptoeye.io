resource "aws_lambda_function_url" "fn_url" {
  function_name      = aws_lambda_function.fn.function_name
  authorization_type = "NONE"
  cors {
    allow_origins = ["*"]
    allow_methods = ["GET"]
    allow_headers = ["*"]
  }
}