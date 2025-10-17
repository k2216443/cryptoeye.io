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

