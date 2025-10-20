# AWS S3 Bucket - Storage for Terraform state files
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket

resource "aws_s3_bucket" "terraform_state" {
  # Required: Name of the S3 bucket
  bucket = var.bucket_name

  # Optional: Map of tags to assign to the bucket
  tags = {
    Name        = "Terraform State Bucket"
    ManagedBy   = "Terraform"
  }
}

# AWS S3 Bucket Versioning - Enables versioning for state file history
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_versioning

resource "aws_s3_bucket_versioning" "terraform_state" {
  # Required: Name of the S3 bucket to apply versioning configuration
  bucket = aws_s3_bucket.terraform_state.id

  # Required: Configuration block for versioning
  versioning_configuration {
    # Required: Versioning state of the bucket (Enabled, Suspended, or Disabled)
    status = "Enabled"
  }
}

# AWS S3 Bucket Server Side Encryption Configuration - Enables encryption at rest
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_server_side_encryption_configuration

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  # Required: Name of the S3 bucket to apply encryption configuration
  bucket = aws_s3_bucket.terraform_state.id

  # Required: Set of server-side encryption configuration rules
  rule {
    # Optional: Single object for setting server-side encryption by default
    apply_server_side_encryption_by_default {
      # Required: Server-side encryption algorithm to use (AES256 or aws:kms)
      sse_algorithm = "AES256"
    }
  }
}

# AWS S3 Bucket Public Access Block - Manages public access block configuration
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_public_access_block

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  # Required: Name of the S3 bucket to apply public access block configuration
  bucket = aws_s3_bucket.terraform_state.id

  # Optional: Whether Amazon S3 should block public ACLs for this bucket
  block_public_acls       = true

  # Optional: Whether Amazon S3 should block public bucket policies for this bucket
  block_public_policy     = true

  # Optional: Whether Amazon S3 should ignore public ACLs for this bucket
  ignore_public_acls      = true

  # Optional: Whether Amazon S3 should restrict public bucket policies for this bucket
  restrict_public_buckets = true
}

# AWS S3 Bucket Lifecycle Configuration - Manages lifecycle rules for object versions
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_lifecycle_configuration

resource "aws_s3_bucket_lifecycle_configuration" "terraform_state" {
  # Required: Name of the S3 bucket to apply lifecycle configuration
  bucket = aws_s3_bucket.terraform_state.id

  # Required: List of configuration blocks describing lifecycle rules
  rule {
    # Required: Unique identifier for the rule
    id     = "expire-old-versions"

    # Required: Whether the rule is currently being applied (Enabled or Disabled)
    status = "Enabled"

    # Optional: Configuration block for expiration of noncurrent versions
    noncurrent_version_expiration {
      # Optional: Number of days after which to expire noncurrent object versions
      noncurrent_days = 90
    }
  }
}

# AWS DynamoDB Table - Provides state locking and consistency checking
# Documentation: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table

resource "aws_dynamodb_table" "terraform_locks" {
  # Required: Name of the DynamoDB table
  name         = var.dynamodb_table_name

  # Optional: Controls how you are charged for read and write throughput
  billing_mode = "PAY_PER_REQUEST"

  # Required: Attribute to use as the hash (partition) key
  hash_key     = "LockID"

  # Required: Set of nested attribute definitions (only for key attributes)
  attribute {
    # Required: Name of the attribute
    name = "LockID"

    # Required: Attribute type (S=string, N=number, B=binary)
    type = "S"
  }

  # Optional: Map of tags to assign to the table
  tags = {
    Name        = "Terraform State Lock Table"
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Terraform Outputs - Export values for use by other configurations
# Documentation: https://developer.hashicorp.com/terraform/language/values/outputs

output "s3_bucket_name" {
  description = "Name of the S3 bucket for Terraform state"
  value       = aws_s3_bucket.terraform_state.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.terraform_state.arn
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for state locking"
  value       = aws_dynamodb_table.terraform_locks.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  value       = aws_dynamodb_table.terraform_locks.arn
}
