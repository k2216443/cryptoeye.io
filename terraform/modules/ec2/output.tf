# Terraform Outputs for EC2 Module
# Documentation: https://developer.hashicorp.com/terraform/language/values/outputs

output "private" {
  value = aws_instance.instance.private_ip
}

output "public" {
  value = aws_instance.instance.public_ip
}
