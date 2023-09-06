group "${cmd}" {
  count = "${count}"

    task "superset" {
      driver = "docker"
      shutdown_delay = "10s"

      config {
        image      = "${ecr_url}/zf/insights:${git_sha}"
        force_pull = true

        port_map = {
          https = 8088
        }
      }

      resources {
        cpu    = 6144
        memory = 8000

        network {
          mbits = 1
          port  "https"{}
        }
      }

      service {
        name = "${app}-superset"
        tags = [
          "superset",
          "no-scrape",
          "traefik.http.routers.${app}-superset.middlewares=redirect-to-https@file",
          "traefik.http.routers.${app}-superset.rule=(Host(`${hostname}.zerofox.com`))",
          "traefik.http.routers.${app}-superset.service=${app}-superset",
          "traefik.http.routers.${app}-superset-https.rule=(Host(`${hostname}.zerofox.com`))",
          "traefik.http.routers.${app}-superset-https.service=${app}-superset",
          "traefik.http.routers.${app}-superset-https.tls=true",
          "traefik.http.services.${app}-superset.loadbalancer.server.scheme=https",
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
        data = <<EOH
{
  "type": "service_account",
  {{ with secret "secret/superset/gcp_insights_sa" }}
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
{{ $private_ip := env "NOMAD_IP_https" }}
{{ $ip_sans := printf "ip_sans=%s" $private_ip }}
{{ with secret "pki/ica/issue/insights" "common_name=insights.service.consul" "alt_names=insights.service.aws-${aws_region}.consul" $ip_sans "format=pem" }}
{{ .Data.certificate }}
{{ .Data.issuing_ca }}
{{ .Data.private_key }}
{{ end }}
EOH

        destination = "$${NOMAD_SECRETS_DIR}/server.bundle.pem"
        change_mode = "restart"
    }

      template {
        data = <<EOH
GOOGLE_APPLICATION_CREDENTIALS=/secrets/service-acct.json

{{ with secret "database/insights-superset-db/creds/admin" }}
DATABASE_URL="postgresql://{{ .Data.username }}:{{ .Data.password }}@${db_address}:${db_port}/insights_superset"
{{ end }}

{{ with secret "secret/superset/insights" }}
SSO_API_BASE_URL="{{ .Data.SSO_API_BASE_URL }}"
SSO_CLIENT_ID="{{ .Data.SSO_CLIENT_ID }}"
SSO_CLIENT_SECRET="{{ .Data.SSO_CLIENT_SECRET }}"
SUPERSET_SECRET_KEY="{{ .Data.SUPERSET_SECRET_KEY }}"
ZF_JWT_PUBLIC_SECRET="{{ .Data.ZF_JWT_TOKEN }}"
{{ end }}


# TODO: delete when values are set in vault
GUEST_TOKEN_JWT_SECRET="SAMPLE"


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
        env = true
        change_mode = "restart"
      }

      vault {
        policies    = ["insights"]
        change_mode = "restart"
      }
    }
  }