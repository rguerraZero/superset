# vim: filetype=hcl
job "superset" {
  datacenters = ["aws-us-west-2-static-ip"]
  type        = "service"

  meta {
    lang = "python"
    proj = "superset"
  }

  update {
    max_parallel     = 1
    min_healthy_time = "30s"
    healthy_deadline = "2m"
  }

  ${superset}

  ${celery_worker_group}

  ${celery_flower_group}

  ${celery_beat_group}
}