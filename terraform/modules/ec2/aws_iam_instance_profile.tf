resource "aws_iam_instance_profile" "ecsInstanceProfile" {
  name = "InstanceProfile-${var.name}"
  role = aws_iam_role.role.name
}
