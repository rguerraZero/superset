variable "app" {
  default = "superset"
}

variable "env" {
  default = "qa"
}

variable "aws_region" {
  default = "us-west-2"
}

variable "git_sha" {
  default = "master"
}

variable "cmd" {
  default = "superset"
}

variable "ecr_url" {
  default = "012321959326.dkr.ecr.us-west-2.amazonaws.com"
}

variable "container_count" {
  type = "map"

  default = {
    qa   = 1
    stag = 1
    prod = 1
  }
}

# ------------------------------------------------------------------------
# Nomad
# ------------------------------------------------------------------------
data "template_file" "nomad_group" {
  template = "${file("./nomad/superset.nomad.hcl")}"

  vars {
    app        = "${var.app}"
    cmd        = "${var.cmd}"
    count      = "${lookup(var.container_count, var.env)}"
    git_sha    = "${var.git_sha}"
    env        = "${var.env}"
    aws_region = "${var.aws_region}"
    ecr_url    = "${var.ecr_url}"
  }
}

output "nomad_group" {
  value = "${data.template_file.nomad_group.rendered}"
}
