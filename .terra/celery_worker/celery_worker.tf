variable "app" {}

variable "env" {}

variable "aws_region" {}

variable "git_sha" {}

variable "cmd" {
  default = "celery-worker"
}

variable "ecr_url" {}

# ----------------------------------------
# AWS
# ----------------------------------------
provider "aws" {
  region = "${var.aws_region}"
}

# ----------------------------------------
# Nomad Configuration
# ----------------------------------------
locals {
  container_counts = {
    qa   = 1
    stag = 1
    prod = 3
  }
}

data "template_file" "nomad_group" {
  template = "${file("./celery_worker/celery_worker.nomad.hcl")}"

  vars {
    aws_region = "${var.aws_region}"
    ecr_url    = "${var.ecr_url}"
    git_sha    = "${var.git_sha}"
    app        = "${var.app}"

    count = "${local.container_counts[var.env]}"
  }
}

output "nomad_group" {
  value = "${data.template_file.nomad_group.rendered}"
}
