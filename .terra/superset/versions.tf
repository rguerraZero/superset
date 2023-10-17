terraform {
  backend "s3" {
    key    = "superset/terraform.tfstate"
    region = "us-west-2"
  }

  required_version = "0.12.31"

  required_providers {
    aws = ">=3.53.0"
    null = "~> 3.1.1"
  }
}
