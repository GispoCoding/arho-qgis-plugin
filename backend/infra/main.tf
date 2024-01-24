terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
    }
  }
}


provider "aws" {
  region = var.AWS_REGION_NAME
}
