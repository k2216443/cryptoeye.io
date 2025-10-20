# Terraform Variable Values - Defines actual values for bucket configuration
# Documentation: https://developer.hashicorp.com/terraform/language/values/variables#variable-definitions-tfvars-files

aws_region          = "us-west-2"
bucket_name         = "chaineye-terraform-state"
dynamodb_table_name = "terraform-state-locks"

