# AWS Route53 Zone - Data source to fetch existing hosted zone
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/route53_zone

data "aws_route53_zone" "chaineye" {
  # Required: Hosted zone name
  name = "chaineye.io."
}

# AWS Route53 Record - DNS record for domain
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route53_record

resource "aws_route53_record" "chaineye" {
  # Required: Hosted zone ID
  zone_id = data.aws_route53_zone.chaineye.zone_id

  # Required: DNS record name
  name = "chaineye.io"

  # Required: DNS record type (A, AAAA, CNAME, etc.)
  type = "A"

  # Optional: Alias record configuration for AWS resources
  alias {
    # Required: DNS name of the target
    name = aws_lb.chaineye.dns_name

    # Required: Hosted zone ID of the target
    zone_id = aws_lb.chaineye.zone_id

    # Required: Whether to evaluate target health
    evaluate_target_health = true
  }
}

# AWS ACM Certificate Validation - Validates SSL certificate using DNS
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/acm_certificate_validation

resource "aws_acm_certificate_validation" "chaineye" {
  # Required: ARN of the certificate to validate
  certificate_arn = aws_acm_certificate.chaineye.arn

  # Optional: List of FQDNs from validation records
  validation_record_fqdns = [for r in aws_route53_record.acm_verification : r.fqdn]
}

# AWS Route53 Record - DNS validation records for ACM certificate
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/route53_record

resource "aws_route53_record" "acm_verification" {
  # Create one record per domain validation option
  for_each = {
    for dvo in aws_acm_certificate.chaineye.domain_validation_options :
    dvo.domain_name => {
      name  = dvo.resource_record_name
      type  = dvo.resource_record_type
      value = dvo.resource_record_value
    }
  }

  # Required: Hosted zone ID
  zone_id = data.aws_route53_zone.chaineye.zone_id

  # Required: DNS record name
  name = each.value.name

  # Required: DNS record type
  type = each.value.type

  # Optional: Time to live in seconds
  ttl = 300

  # Required: List of record values
  records = [each.value.value]
}
