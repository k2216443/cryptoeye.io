resource "aws_acm_certificate" "chaineye" {
  domain_name       = "chaineye.io"
  validation_method = "DNS"
  lifecycle {
    create_before_destroy = true
  }
  tags = {
    Name = "chaineye.io"
  }
}
