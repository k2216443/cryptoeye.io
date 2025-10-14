resource "aws_eip" "eip" {
  count    = var.expose ? 1 : 0
  instance = aws_instance.instance.id

  tags = {
    Name = var.name
  }
}
