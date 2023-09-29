terraform {
  backend "s3" {
    key    = "insights/terraform.tfstate"
    region = "us-west-2"
  }

  required_version = "0.12.31"
}
