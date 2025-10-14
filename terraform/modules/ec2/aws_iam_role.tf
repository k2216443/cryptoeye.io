resource "aws_iam_role" "role" {
  name               = "ecsInstanceRole-${var.name}"
  assume_role_policy = var.ecsInstanceRoleAssumeRolePolicy
}


variable "ecsInstanceRoleAssumeRolePolicy" {
  type = string

  default = <<EOF
{
  "Version": "2008-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "ecsInstanceRolePolicy" {
  name   = "ecsInstanceRolePolicy-${var.name}"
  role   = aws_iam_role.role.id
  policy = var.policy
}
