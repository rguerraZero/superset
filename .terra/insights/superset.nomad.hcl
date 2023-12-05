# vim: filetype=hcl
job "insights" {
  datacenters = ["aws-us-west-2-customer"]
  type        = "service"

  meta {
    lang = "python"
    proj = "insights"
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