data "aws_vpc" "vpc" {
  filter {
    name   = "tag:Name"
    values = [var.vpc]
  }
}

data "aws_subnet" "subnet" {
  filter {
    name   = "tag:Name"
    values = [var.subnet]
  }
}
