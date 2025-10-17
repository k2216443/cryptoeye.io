data "aws_route53_zone" "chaineye" {
  name = "chaineye.io."
}

resource "aws_route53_record" "chaineye" {
  zone_id = data.aws_route53_zone.chaineye.zone_id
  name    = "chaineye.io"
  type    = "A"

  alias {
    name                   = aws_lb.chaineye.dns_name
    zone_id                = aws_lb.chaineye.zone_id
    evaluate_target_health = true
  }
}

resource "aws_acm_certificate_validation" "chaineye" {
  certificate_arn         = aws_acm_certificate.chaineye.arn
  validation_record_fqdns = [for r in aws_route53_record.acm_verification : r.fqdn]
}

resource "aws_route53_record" "acm_verification" {
  for_each = {
    for dvo in aws_acm_certificate.chaineye.domain_validation_options :
    dvo.domain_name => {
      name  = dvo.resource_record_name
      type  = dvo.resource_record_type
      value = dvo.resource_record_value
    }
  }

  zone_id = data.aws_route53_zone.chaineye.zone_id
  name    = each.value.name
  type    = each.value.type
  ttl     = 300
  records = [each.value.value]
}