# AWS Provider Configuration - Configures AWS provider for resource management
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs

provider "aws" {
  # Optional: AWS region where resources will be managed
  region = "us-west-2"

  # Optional: AWS CLI named profile containing credentials
  profile = "cryptoeye"
}

