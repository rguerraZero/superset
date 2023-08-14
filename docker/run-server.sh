#!/usr/bin/env bash
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
HYPHEN_SYMBOL='-'

if [[ -f ${NOMAD_SECRETS_DIR}/server.bundle.pem ]]; then
    cp ${NOMAD_SECRETS_DIR}/server.bundle.pem /app/server.bundle.pem
    csplit -f server. -b '%01d.pem' /app/server.bundle.pem '/BEGIN EC PRIVATE KEY/'
    mv /app/server.0.pem /app/server.crt
    mv /app/server.1.pem /app/server.key
else
    echo 'certificate bundle not present'
fi

gunicorn \
    --bind "${SUPERSET_BIND_ADDRESS:-0.0.0.0}:${SUPERSET_PORT:-8088}" \
    --certfile "${SUPERSET_CERTFILE:-$HYPHEN_SYMBOL}" \
    --keyfile "${SUPERSET_KEYFILE:-$HYPHEN_SYMBOL}" \
    --access-logfile "${ACCESS_LOG_FILE:-$HYPHEN_SYMBOL}" \
    --error-logfile "${ERROR_LOG_FILE:-$HYPHEN_SYMBOL}" \
    --workers ${SERVER_WORKER_AMOUNT:-1} \
    --worker-class ${SERVER_WORKER_CLASS:-gthread} \
    --threads ${SERVER_THREADS_AMOUNT:-20} \
    --timeout ${GUNICORN_TIMEOUT:-60} \
    --keep-alive ${GUNICORN_KEEPALIVE:-2} \
    --max-requests ${WORKER_MAX_REQUESTS:-0} \
    --max-requests-jitter ${WORKER_MAX_REQUESTS_JITTER:-0} \
    --limit-request-line ${SERVER_LIMIT_REQUEST_LINE:-0} \
    --limit-request-field_size ${SERVER_LIMIT_REQUEST_FIELD_SIZE:-0} \
    "${FLASK_APP}"
