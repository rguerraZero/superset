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

variable "ecr_url" {
  default = "012321959326.dkr.ecr.us-west-2.amazonaws.com"
}

variable "consul_token" {
  default = ""
}

variable "zf_api_host" {
  type = map(string)

  default = {
    qa   = "https://api.zerofox.com"
    stag = "https://api.zerofox.com"
    prod = "https://api.zerofox.com"
  }
}

variable "global_async_queries" {
  type = map(string)

  default = {
    qa   = "False"
    stag = "False"
    prod = "False"
  }
}

# ----------------------------------------
# Providers
# ----------------------------------------
provider "nomad" {
  address = "https://nomad-${var.env}.zerofox.com"
  region  = "global"
}

provider "consul" {
  address    = "consul-${var.env}.zerofox.com:443"
  datacenter = "aws-${var.aws_region}"
  scheme     = "https"
}

data "terraform_remote_state" "global" {
  backend = "s3"

  config = {
    bucket = "zf-terraform-global"
    key    = "global/terraform.tfstate"
    region = "us-west-2"
  }
}

# ----------------------------------------
# Superset + Celery Worker + Beat
# ----------------------------------------
resource "aws_elasticache_cluster" "cache" {
  cluster_id           = "${var.app}-${var.env}-cache"
  engine               = "redis"
  engine_version       = "5.0.6"
  node_type            = "cache.t3.small"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis5.0"
  subnet_group_name    = "west-redis"

  # TF-UPGRADE-TODO: In Terraform v0.10 and earlier, it was sometimes necessary to
  # force an interpolation expression to be interpreted as a list by wrapping it
  # in an extra set of list brackets. That form was supported for compatibility in
  # v0.11, but is no longer supported in Terraform v0.12.
  #
  # If the expression in the following list itself returns a list, remove the
  # brackets to avoid interpretation as a list of lists. If the expression
  # returns a single list item then leave it as-is and remove this TODO comment.
  security_group_ids = [
    data.terraform_remote_state.global.outputs.corporate_sg_ids[var.aws_region],
  ]

  tags = {
    Application = var.app
    Environment = var.env
  }
}

module "celery_worker" {
  source = "./celery_worker"

  app        = var.app
  env        = var.env
  git_sha    = var.git_sha
  aws_region = var.aws_region
  ecr_url    = var.ecr_url
}

module "celery_beat" {
  source = "./celery_beat"

  app        = var.app
  env        = var.env
  git_sha    = var.git_sha
  aws_region = var.aws_region
  ecr_url    = var.ecr_url
}

module "celery_flower" {
  source = "./celery_flower"

  app        = var.app
  env        = var.env
  git_sha    = var.git_sha
  aws_region = var.aws_region
  ecr_url    = var.ecr_url
}

module "superset" {
  source = "./nomad"

  app        = var.app
  env        = var.env
  git_sha    = var.git_sha
  aws_region = var.aws_region
  ecr_url    = var.ecr_url
}

# ------------------------------------------------------------------------
# Nomad
# ------------------------------------------------------------------------
data "template_file" "nomad_job_spec" {
  template = file("superset.nomad.hcl")

  vars = {
    celery_worker_group = module.celery_worker.nomad_group
    celery_beat_group   = module.celery_beat.nomad_group
    celery_flower_group = module.celery_flower.nomad_group
    superset            = module.superset.nomad_group
  }
}

module "nomad-job" {
  source = "git::ssh://git@github.com/riskive/devops-terraform-modules.git//nomad-build-run?ref=master"

  app               = var.app
  ecr_url           = var.ecr_url
  git_sha           = var.git_sha
  docker_file       = "../../Dockerfile"
  docker_path       = "../.."
  rendered_template = data.template_file.nomad_job_spec.rendered
}

resource "consul_keys" "superset-keys" {
  datacenter = "aws-${var.aws_region}"
  token      = var.consul_token

  key {
    path  = "${var.app}/superset/env/redis_host"
    value = aws_elasticache_cluster.cache.cache_nodes[0].address
  }

  key {
    path  = "${var.app}/superset/env/redis_port"
    value = aws_elasticache_cluster.cache.cache_nodes[0].port
  }

  key {
    path  = "${var.app}/superset/env/env"
    value = var.env
  }

  key {
    path  = "${var.app}/superset/env/server_limit_request_field_size"
    value = "8190"
  }

  key {
    path  = "${var.app}/superset/env/server_limit_request_line"
    value = "4094"
  }

  key {
    path  = "${var.app}/superset/env/server_limit_request_fields"
    value = "20"
  }

  key {
    path  = "${var.app}/superset/env/gunicorn_timeout"
    value = "300"
  }

  key {
    path  = "${var.app}/superset/env/server_worker_amount"
    value = "6"
  }

  key {
    path  = "${var.app}/superset/env/superset_certfile"
    value = "/app/server.crt"
  }

  key {
    path  = "${var.app}/superset/env/superset_keyfile"
    value = "/app/server.key"
  }

  key {
    path  = "${var.app}/superset/env/gunicorn_keepalive"
    value = "65"
  }

  key {
    path  = "${var.app}/superset/env/superset_access_method"
    value = "internal"
  }

  key {
    path  = "${var.app}/superset/env/bq_dataset"
    value = "csdataanalysis"
  }

  key {
    path  = "${var.app}/superset/env/zf_api_host"
    value = var.zf_api_host[var.env]
  }

  key {
    path  = "${var.app}/superset/env/global_async_queries"
    value = var.global_async_queries[var.env]
  }

  key {
    path  = "${var.app}/superset/env/global_async_queries_jwt_cookie_domain"
    value = "superset-${var.env}.zerofox.com"
  }
}

module "pdfs_bucket" {
  source     = "git::ssh://git@github.com/riskive/devops-terraform-modules.git//s3-bucket?ref=fix-s3-bucket"
  name       = "superset-internal-pdfs-${var.env}"
  app        = var.app
  env        = var.env
  public     = false
  dr_enabled = false
}

resource "aws_s3_bucket_lifecycle_configuration" "lifecycle" {
  count  = 1
  bucket = module.pdfs_bucket.bucket_name
  rule {
    id = "bucket-dr"
    expiration {
      days = 1
    }
    status = "Enabled"
  }
}

# https://docs.aws.amazon.com/AmazonS3/latest/dev/example-bucket-policies.html
# https://aws.amazon.com/blogs/security/iam-policies-and-bucket-policies-and-acls-oh-my-controlling-access-to-s3-resources/
resource "aws_s3_bucket_policy" "private" {
  count  = 1
  bucket = module.pdfs_bucket.bucket_name
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "${module.pdfs_bucket.bucket_arn}/*"
    },
    {
      "Sid": "AllowSSLRequestsOnly",
      "Action": "s3:*",
      "Effect": "Deny",
      "Resource": [
        "${module.pdfs_bucket.bucket_arn}",
        "${module.pdfs_bucket.bucket_arn}/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      },
      "Principal": "*"
    }
  ]
}
POLICY
}
