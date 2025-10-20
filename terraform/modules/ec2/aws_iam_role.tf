# AWS IAM Role - Identity and Access Management role for EC2 instances
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role

resource "aws_iam_role" "role" {
  # Required: Role name
  name = "ecsInstanceRole-${var.name}"

  # Required: Assume role policy document (JSON)
  assume_role_policy = var.ecsInstanceRoleAssumeRolePolicy
}

# Terraform Variables for IAM Role
# Documentation: https://developer.hashicorp.com/terraform/language/values/variables

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

# AWS IAM Role Policy - Inline policy attached to IAM role
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy

resource "aws_iam_role_policy" "ecsInstanceRolePolicy" {
  # Optional: Policy name
  name = "ecsInstanceRolePolicy-${var.name}"

  # Required: IAM role ID to attach policy to
  role = aws_iam_role.role.id

  # Required: Policy document in JSON format
  policy = var.policy
}
