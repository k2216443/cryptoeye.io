# Terraform Configuration - Backend and required providers
# Documentation: https://developer.hashicorp.com/terraform/language/settings

terraform {
  backend "s3" {
    # Required: Name of the S3 bucket where the Terraform state file will be stored
    bucket = "chaineye-terraform-state"

    # Required: Path inside the S3 bucket where the state file will reside
    key = "chaineye.tfstate"

    # Required: AWS region where the S3 bucket is located
    region = "us-west-2"

    # Optional: AWS credentials profile
    profile = "cryptoeye"
  }
}

# AWS Provider - Configure AWS provider with region and authentication
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs

provider "aws" {
  # Required: AWS region where resources will be managed
  region = "us-west-2"

  # Optional: AWS CLI named profile containing credentials
  profile = "cryptoeye"
}
