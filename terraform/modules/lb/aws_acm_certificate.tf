# AWS ACM Certificate - SSL/TLS certificate for HTTPS
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/acm_certificate

resource "aws_acm_certificate" "chaineye" {
  # Required: Domain name for the certificate
  domain_name = "chaineye.io"

  # Required: Certificate validation method (DNS or EMAIL)
  validation_method = "DNS"

  # Optional: Lifecycle configuration
  lifecycle {
    # Create new certificate before destroying old one
    create_before_destroy = true
  }

  # Optional: Resource tags
  tags = {
    Name = "chaineye.io"
  }
}
