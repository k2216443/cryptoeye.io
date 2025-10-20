# AWS Key Pair - SSH key pair for EC2 instance access
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/key_pair

resource "aws_key_pair" "chaineye" {
  # Required: Name for the key pair
  key_name   = "chaineye"

  # Required: Public key material in OpenSSH format
  public_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDCaLB8SScfyzbI4UwVhx1jGwBwICIofzHtGa1ozLr9d k2216443-tencent-2024-07-26"
}

