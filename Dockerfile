#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

######################################################################
# Node stage to deal with static asset construction
######################################################################
ARG PY_VER=3.8.16-slim
FROM node:16-slim AS superset-node

ARG NPM_BUILD_CMD="build"
ARG ASSET_BASE_URL
ENV BUILD_CMD=${NPM_BUILD_CMD}
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

# NPM ci first, as to NOT invalidate previous steps except for when package.json changes
RUN mkdir -p /app/superset-frontend

COPY ./docker/frontend-mem-nag.sh /
RUN /frontend-mem-nag.sh

RUN apt-get update || : && apt-get install -y \
    python3 \
    build-essential

WORKDIR /app/superset-frontend/

COPY superset-frontend/package*.json ./
RUN npm ci

COPY ./superset-frontend .

# This seems to be the most expensive step
RUN ASSET_BASE_URL=${ASSET_BASE_URL} npm run ${BUILD_CMD} --verbose

######################################################################
# Final lean image...
######################################################################
FROM python:${PY_VER} AS lean

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    FLASK_ENV=production \
    FLASK_APP="superset.app:create_app()" \
    PYTHONPATH="/app/pythonpath" \
    SUPERSET_HOME="/app/superset_home" \
    SUPERSET_PORT=8088 \
    GECKODRIVER_VERSION=0.29.0

RUN mkdir -p ${PYTHONPATH} \
    && useradd --user-group -d ${SUPERSET_HOME} -m --no-log-init --shell /bin/bash superset \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    default-libmysqlclient-dev \
    libsasl2-dev \
    libsasl2-modules-gssapi-mit \
    libpq-dev \
    libecpg-dev \
    firefox-esr \
    wget \
    unzip \
    telnet \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz && \
    tar -x geckodriver -zf geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz -O > /usr/bin/geckodriver && \
    chmod 755 /usr/bin/geckodriver && \
    rm geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz

COPY ./requirements/*.txt  /app/requirements/
COPY setup.py MANIFEST.in README.md /app/

# setup.py uses the version information in package.json
COPY superset-frontend/package.json /app/superset-frontend/

RUN cd /app \
    && mkdir -p superset/static \
    && touch superset/static/version_info.json \
    && pip install --no-cache -r requirements/local.txt

COPY --from=superset-node /app/superset/static/assets /app/superset/static/assets

## Lastly, let's install superset itself
COPY superset /app/superset
COPY setup.py MANIFEST.in README.md /app/
COPY ./docker/run-server.sh /usr/bin/run-server.sh
RUN chmod a+x /usr/bin/run-server.sh

RUN cd /app \
    && chown -R superset:superset /app \
    && pip install -e . \
    && flask fab babel-compile --target superset/translations

WORKDIR /app
USER superset

# Copy BI Superset
COPY bi_superset/ /app/bi_superset/
COPY bi_superset/superset_config.py /app/superset_config.py

# Injects bi_cli into superset cli
COPY bi_superset/bi_cli/bi_cli.py /app/superset/cli/bi_cli.py

# Copy ZF-Dashboard integration files
COPY zf_integration/ /app/superset/zf_integration/
COPY zf_utils/jwt.py /app/superset/utils/jwt.py

HEALTHCHECK CMD curl -f "http://localhost:$SUPERSET_PORT/health"

EXPOSE ${SUPERSET_PORT}

CMD /usr/bin/run-server.sh
