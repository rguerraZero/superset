# vim: filetype=hcl
job "insights" {
  datacenters = ["aws-us-west-2-customer"]
  type        = "service"

  meta {
    lang = "python"
    proj = "insights"
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