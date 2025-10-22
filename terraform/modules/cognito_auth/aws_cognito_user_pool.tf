
resource "aws_cognito_user_pool" "this" {
  name = "${local.name}-users"

  username_attributes        = ["email"]
  auto_verified_attributes   = ["email"]
  mfa_configuration          = "OFF"
  deletion_protection        = "ACTIVE"
  account_recovery_setting {
    recovery_mechanism { name = "verified_email", priority = 1 }
  }

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = false
    require_uppercase = true
    temporary_password_validity_days = 7
  }

  verification_message_template {
    default_email_option   = "CONFIRM_WITH_LINK"
    email_subject_by_link  = "Confirm your sign up"
    email_message_by_link  = "Click the link to confirm your account: {##Verify Email##}"
  }

  admin_create_user_config {
    allow_admin_create_user_only = false
  }

  user_attribute_update_settings {
    attributes_require_verification_before_update = ["email"]
  }

  tags = merge(var.tags, {
    Module = "cognito_auth"
    Name   = local.name
  })
}

