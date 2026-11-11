# Bucket for transferring large plan files (import/export) between clients and
# the ryhti_client lambda via presigned URLs. Objects are temporary and expire
# automatically.
resource "aws_s3_bucket" "ryhti_files" {
  bucket        = "${var.prefix}-ryhti-files"
  # Bucket only contains temporary transfer files, so it is safe to destroy
  force_destroy = true

  tags = merge(local.default_tags, { Name = "${var.prefix}-ryhti-files" })
}

resource "aws_s3_bucket_public_access_block" "ryhti_files" {
  bucket                  = aws_s3_bucket.ryhti_files.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "ryhti_files" {
  bucket = aws_s3_bucket.ryhti_files.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# SSE-S3 (not KMS) so presigned GET/PUT URLs work without kms permissions
resource "aws_s3_bucket_server_side_encryption_configuration" "ryhti_files" {
  bucket = aws_s3_bucket.ryhti_files.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "ryhti_files" {
  bucket = aws_s3_bucket.ryhti_files.id
  rule {
    id     = "expire-transfer-files"
    status = "Enabled"
    filter {}
    expiration {
      days = 1
    }
    abort_incomplete_multipart_upload {
      days_after_initiation = 1
    }
  }
}
