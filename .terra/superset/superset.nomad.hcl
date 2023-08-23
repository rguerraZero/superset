# vim: filetype=hcl
job "superset" {
  datacenters = ["aws-us-west-2-static-ip"]
  type        = "service"

  meta {
    lang = "python"
    proj = "superset"
  }

  update {
    stagger      = "10s"
    max_parallel = 1
  }

  ${superset}

  ${celery_worker_group}

  ${celery_flower_group}

  ${celery_beat_group}
}