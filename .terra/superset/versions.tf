terraform {
  backend "s3" {
    key    = "superset/terraform.tfstate"
    region = "us-west-2"
  }

  required_version = "0.11.15"
}
