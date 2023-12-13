group "${cmd}" {
  count = "${count}"

  meta {
    group = "${cmd}"
    index_name  = "superset-${cmd}"
    index_type  = "python"
  }

  task "superset" {
    driver         = "docker"
    shutdown_delay = "10s"

    meta {
      node_filebeat = true
    }

    config {
      image      = "${ecr_url}/zf/superset:${git_sha}"
      force_pull = true

      port_map = {
        https = 8088
      }
    }

    resources {
      cpu    = 6144
      memory = 10000

      network {
        mbits = 1
        port "https" {}
      }
    }

    service {
      name = "$${NOMAD_TASK_NAME}"
      tags = [
        "https",
        "prometheus-https",
        "superset",
        "https",
        "urlprefix-superset-${env}.zerofox.com/ proto=https",
        "cs=zerofox",
        "traefik.http.routers.$${NOMAD_TASK_NAME}.middlewares=redirect-to-https@file",
        "traefik.http.routers.$${NOMAD_TASK_NAME}.rule=Host(`superset-${env}.zerofox.com`)",
        "traefik.http.routers.$${NOMAD_TASK_NAME}.service=$${NOMAD_TASK_NAME}",
        "traefik.http.routers.$${NOMAD_TASK_NAME}-https.rule=Host(`superset-${env}.zerofox.com`)",
        "traefik.http.routers.$${NOMAD_TASK_NAME}-https.service=$${NOMAD_TASK_NAME}",
        "traefik.http.routers.$${NOMAD_TASK_NAME}-https.tls=true",
        "traefik.http.services.$${NOMAD_TASK_NAME}.loadbalancer.server.scheme=https",
      ]
      port = "https"

      check {
        type     = "tcp"
        port     = "https"
        interval = "30s"
        timeout  = "2s"
      }
    }

    template {
      data        = <<EOH
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
      change_mode = "restart"
    }

    template {
      data = <<EOH
{{ $private_ip := env "NOMAD_IP_https" }}
{{ $ip_sans := printf "ip_sans=%s" $private_ip }}
{{ with secret "pki/ica/issue/superset" "common_name=superset.service.consul" "alt_names=superset.service.aws-${aws_region}.consul" $ip_sans "format=pem" }}
{{ .Data.certificate }}
{{ .Data.issuing_ca }}
{{ .Data.private_key }}
{{ end }}
EOH

      destination = "$${NOMAD_SECRETS_DIR}/server.bundle.pem"
      change_mode = "restart"
    }

    template {
      data        = <<EOH
GOOGLE_APPLICATION_CREDENTIALS=/secrets/service-acct.json

{{ with secret "secret/superset/database_url" }}
DATABASE_URL="postgresql+psycopg2://{{ .Data.value }}"
SSO_API_BASE_URL="{{ .Data.SSO_API_BASE_URL }}"
SSO_CLIENT_ID="{{ .Data.SSO_CLIENT_ID }}"
SSO_CLIENT_SECRET="{{ .Data.SSO_CLIENT_SECRET }}"
SUPERSET_SECRET_KEY="{{ .Data.SUPERSET_SECRET_KEY }}"
{{ end }}

{{ with secret "secret/superset/configuration" }}
GLOBAL_ASYNC_QUERIES_JWT_SECRET="{{ .Data.GLOBAL_ASYNC_QUERIES_JWT_SECRET }}"
{{ end }}


# TODO: delete when values are set in vault
GUEST_TOKEN_JWT_SECRET="SAMPLE"
ZF_JWT_PUBLIC_SECRET="SAMPLE_2"

{{ with secret "secret/smtp" }}
SENDGRID_HOST="{{ .Data.host }}"
SENDGRID_PORT="{{ .Data.port }}"
SENDGRID_USERNAME="{{ .Data.username }}"
SENDGRID_PASSWORD="{{ .Data.password }}"{{ end }}

{{ range ls "${app}/superset/env" }}
{{ .Key|toUpper }}="{{ .Value }}"
{{ end }}

{{ with secret "aws/sts/${app}" "ttl=24h"}}
AWS_REGION="${aws_region}"
AWS_ACCESS_KEY_ID="{{ .Data.access_key }}"
AWS_SECRET_ACCESS_KEY="{{ .Data.secret_key }}"
AWS_SESSION_TOKEN="{{ .Data.security_token }}"{{ end }}

EOH
      destination = "secrets/env"
      env         = true
      change_mode = "restart"
    }

    vault {
      policies    = ["superset"]
      change_mode = "restart"
    }
  }
}