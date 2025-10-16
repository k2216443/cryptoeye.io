resource "aws_lb_target_group_attachment" "backend_instance" {
  target_group_arn = aws_lb_target_group.backend.arn
  target_id        = module.ec2.instance-id
  port             = 8080
}