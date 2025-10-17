# Terraform State S3 Bucket

This Terraform configuration creates an S3 bucket with versioning enabled to store Terraform state files securely.

## Features

- **S3 Bucket** with versioning enabled
- **Server-side encryption** (AES256)
- **Public access blocked** for security
- **Lifecycle policy** to expire old versions after 90 days
- **DynamoDB table** for state locking to prevent concurrent modifications

## Usage

### 1. Initial Setup

Copy the example variables file and update with your values:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and set your desired bucket name (must be globally unique):

```hcl
bucket_name = "your-unique-bucket-name-terraform-state"
aws_region  = "us-east-1"
```

### 2. Deploy the Infrastructure

```bash
terraform init
terraform plan
terraform apply
```

### 3. Configure Your Main Project

After the bucket is created, configure your main Terraform project to use this backend by adding to your main project's configuration:

```hcl
terraform {
  backend "s3" {
    bucket         = "your-unique-bucket-name-terraform-state"
    key            = "path/to/your/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-locks"
  }
}
```

Then migrate your state:

```bash
terraform init -migrate-state
```

## Important Notes

- **Bucket Name**: Must be globally unique across all AWS accounts
- **Versioning**: Keeps history of state file changes (old versions expire after 90 days)
- **State Locking**: DynamoDB table prevents concurrent state modifications
- **Security**: Public access is blocked and encryption is enabled by default

## Outputs

After applying, you'll see:
- `s3_bucket_name`: The name of your state bucket
- `s3_bucket_arn`: The ARN of the bucket
- `dynamodb_table_name`: The DynamoDB table name for locking
- `dynamodb_table_arn`: The ARN of the DynamoDB table
