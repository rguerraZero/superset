group "celery-flower-group" {
  count = "${count}"

  meta {
    group = "$${NOMAD_GROUP_NAME}"
    lang  = "python"
  }

  task "celery-flower" {
    driver = "docker"
    shutdown_delay = "10s"

    config {
      image   = "${ecr_url}/zf/superset:${git_sha}"
      command = "celery"
      args = [
        "--app=superset.tasks.celery_app:app",
        "flower",
      ]
      force_pull = true
      port_map = {
          https = 5555
        }
    }

    resources {
      cpu    = 1024
      memory = 1024

      network {
        mbits = 1
        port "https" {}
      }
    }

    service {
      name = "$${NOMAD_JOB_NAME}-$${NOMAD_GROUP_NAME}"
      port = "https"

      check {
        name     = "$${NOMAD_JOB_NAME}-$${NOMAD_GROUP_NAME} up check"
        type     = "script"
        command  = "celery"
        args     = [
          "inspect",
          "ping"
        ]
        interval = "30s"
        timeout  = "10s"
      }
    }
  template {
     data = <<EOH
{
  "type": "service_account",
  {{ with secret "secret/cshe/bq-service-acct" }}
  "project_id": "{{ .Data.project_id }}",
  "private_key_id": "{{ .Data.private_key_id }}",
  "private_key": "{{ .Data.private_key }}",
  "client_email": "{{ .Data.client_email }}",
  "client_id": "{{ .Data.client_id }}",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "{{ .Data.client_x509_cert_url }}"{{ end }}
}
EOH
        destination = "secrets/service-acct.json"
        change_mode="restart"
      }

    template {
      data = <<EOH
GOOGLE_APPLICATION_CREDENTIALS=/secrets/service-acct.json

{{ with secret "secret/superset/database_url" }}
DATABASE_URL="postgresql+psycopg2://{{ .Data.value }}"
SSO_API_BASE_URL="{{ .Data.SSO_API_BASE_URL }}"
SSO_CLIENT_ID="{{ .Data.SSO_CLIENT_ID }}"
SSO_CLIENT_SECRET="{{ .Data.SSO_CLIENT_SECRET }}"
SUPERSET_SECRET_KEY="{{ .Data.SUPERSET_SECRET_KEY }}"
{{ end }}

{{ with secret "secret/smtp" }}
SENDGRID_HOST="{{ .Data.host }}"
SENDGRID_PORT="{{ .Data.port }}"
SENDGRID_USERNAME="{{ .Data.username }}"
SENDGRID_PASSWORD="{{ .Data.password }}"{{ end }}

{{ range ls "${app}/superset/env" }}
{{ .Key|toUpper }}="{{ .Value }}"
{{ end }}
      EOH
      destination = "secrets/env"
      change_mode = "restart"
      env         = true
    }

    vault {
      policies    = ["${app}"]
      change_mode = "restart"
    }
  }
}