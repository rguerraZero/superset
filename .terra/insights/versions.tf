terraform {
  backend "s3" {
    key    = "insights/terraform.tfstate"
    region = "us-west-2"
  }

  required_version = "0.14.10"
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
    consul = {
      source = "hashicorp/consul"
    }
    nomad = {
      source = "hashicorp/nomad"
    }
    template = {
      source = "hashicorp/template"
    }
  }
}
