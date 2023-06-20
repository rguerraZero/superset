#!/bin/bash

if [[ -f ${NOMAD_SECRETS_DIR}/server.bundle.pem ]]; then
    csplit -f server. -b '%01d.pem' ${NOMAD_SECRETS_DIR}/server.bundle.pem '/BEGIN EC PRIVATE KEY/'
    mv server.0.pem ${NOMAD_SECRETS_DIR}/server.crt
    mv server.1.pem ${NOMAD_SECRETS_DIR}/server.key
else
    echo 'certificate bundle not present'
fi



gunicorn "superset.app:create_app()"