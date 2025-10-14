output "private" {
  value = aws_instance.instance.private_ip
}

output "public" {
  value = aws_instance.instance.public_ip
}