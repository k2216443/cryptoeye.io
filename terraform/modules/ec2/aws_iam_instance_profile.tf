# AWS IAM Instance Profile - Container for IAM role attached to EC2 instance
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_instance_profile

resource "aws_iam_instance_profile" "ecsInstanceProfile" {
  # Optional: Instance profile name
  name = "InstanceProfile-${var.name}"

  # Required: IAM role name to attach to profile
  role = aws_iam_role.role.name
}
