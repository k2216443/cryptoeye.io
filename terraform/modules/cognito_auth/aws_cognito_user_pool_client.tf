provider "aws" {
  region = var.region
}

locals {
  name = "${var.project}-${var.env}"
}

resource "aws_cognito_user_pool_client" "web" {
  name         = "${local.name}-web"
  user_pool_id = aws_cognito_user_pool.this.id
                     
  # SPA / PKCE
  generate_secret = false
  prevent_user_existence_errors = "ENABLED"

  supported_identity_providers = ["COGNITO", aws_cognito_identity_provider.google.provider_name]

  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  allowed_oauth_flows_user_pool_client = true
  callback_urls                        = var.callback_urls
  logout_urls                          = var.logout_urls

  access_token_validity  = 60   # minutes
  id_token_validity      = 60
  refresh_token_validity = 30   # days
  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]
}



# Helpful data/locals for outputs
locals {
  hosted_ui_base       = "https://${aws_cognito_user_pool_domain.this.domain}.auth.${var.region}.amazoncognito.com"
  oauth_authorize_url  = "${local.hosted_ui_base}/oauth2/authorize"
  oauth_token_url      = "${local.hosted_ui_base}/oauth2/token"
  jwks_url             = "https://cognito-idp.${var.region}.amazonaws.com/${aws_cognito_user_pool.this.id}/.well-known/jwks.json"
  issuer_url           = "https://cognito-idp.${var.region}.amazonaws.com/${aws_cognito_user_pool.this.id}"
}
