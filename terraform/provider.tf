# Terraform Configuration for AWS

# --- AWS Provider Configuration ---

# The provider block is used to configure the named provider, in this case, AWS.
provider "aws" {
  # Specify the AWS region where resources will be managed.
  # "us-west-2" is the AWS code for the Oregon region.
  region = "us-west-2"

  # Reference to the AWS CLI named profile. This profile should be configured in your 
  # AWS CLI setup and contains the necessary credentials to interact with AWS.
  # Using named profiles helps in managing multiple AWS configurations and accounts.
  profile = "cryptoeye"
}

# --- Terraform Backend Configuration ---

# The backend block configures where Terraform's state files will be stored.
# State files track the configurations deployed, so it's crucial to keep them consistent and safe.
# Here, the state file is stored in an AWS S3 bucket.
terraform {
  backend "s3" {

    # Name of the S3 bucket where the Terraform state file will be stored.
    bucket = "chaineye-terraform-state"

    # Path inside the S3 bucket where the state file will reside.
    # Organizing state files by environment or function can make managing multiple state files easier.
    key = "chaineye.tfstate"

    # AWS region where the S3 bucket is located.
    region = "us-west-2"

    # AWS credentials profile
    profile = "cryptoeye"
  }
}
