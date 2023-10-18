terraform {
  backend "s3" {
    key    = "superset/terraform.tfstate"
    region = "us-west-2"
  }

  required_version = ">= 0.13"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">=3.53.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3.1.1"
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
