ARG NODE_VERSION=16
ARG PYTHON_VERSION=3.8

FROM python:$PYTHON_VERSION

# Configure environment
# superset recommended defaults: https://superset.apache.org/docs/installation/configuring-superset#running-on-a-wsgi-http-server
# gunicorn recommended defaults: https://docs.gunicorn.org/en/0.17.2/configure.html#security
ARG SUPERSET_VERSION=2.1.0
ENV FLASK_ENV=testing
ENV FLASK_APP=superset
ENV GUNICORN_BIND=0.0.0.0:8088
ENV GUNICORN_LIMIT_REQUEST_FIELD_SIZE=8190
ENV GUNICORN_LIMIT_REQUEST_LINE=4094
ENV GUNICORN_THREADS=20
ENV GUNICORN_TIMEOUT=300
ENV GUNICORN_WORKERS=6
ENV GUNICORN_WORKER_CLASS=gthread
ENV GUNICORN_CERT=/secrets/server.crt
ENV GUNICORN_KEY=/secrets/server.key
ENV GUNICORN_KEEPALIVE=65
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONPATH=/etc/superset:/home/superset:/:$PYTHONPATH
ENV SUPERSET_REPO=apache/superset
ENV SUPERSET_HOME=/var/lib/superset
ENV SUPERSET_VERSION=$SUPERSET_VERSION
ENV SUPERSET_CONFIG_PATH=/superset_config.py
ENV GECKODRIVER_VERSION=0.29.0
ENV GUNICORN_CMD_ARGS="--bind $GUNICORN_BIND --certfile $GUNICORN_CERT --keyfile $GUNICORN_KEY --limit-request-field_size $GUNICORN_LIMIT_REQUEST_FIELD_SIZE --limit-request-line $GUNICORN_LIMIT_REQUEST_LINE --threads $GUNICORN_THREADS --timeout $GUNICORN_TIMEOUT --workers $GUNICORN_WORKERS --worker-class $GUNICORN_WORKER_CLASS --keep-alive $GUNICORN_KEEPALIVE"

RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y autoclean && \
    apt-get -y clean all

# Create superset user & install dependencies
WORKDIR /home/superset
COPY requirements*.txt ./
RUN groupadd supergroup && \
    useradd -U -G supergroup superset && \
    chown superset:superset /home/superset && \
    mkdir -p /etc/superset && \
    mkdir -p $SUPERSET_HOME && \
    chown -R superset:superset /etc/superset && \
    chown -R superset:superset $SUPERSET_HOME && \
    apt-get update && \
    apt-get install -y \
    build-essential \
    curl \
    default-libmysqlclient-dev \
    freetds-bin \
    freetds-dev \
    libaio1 \
    libecpg-dev \
    libffi-dev \
    libldap2-dev \
    libpq-dev \
    libsasl2-2 \
    libsasl2-dev \
    libsasl2-modules-gssapi-mit \
    libssl-dev && \
    openssl && \
    apt-get clean && \
    pip install apache-superset==$SUPERSET_VERSION && \
    pip uninstall -y markupsafe && \
    pip install markupsafe==2.0.1 && \
    pip uninstall -y Werkzeug && \
    pip install Werkzeug==2.0.3 && \
    pip install flask==2.1.3 && \
    pip install Flask-WTF && \
    pip install WTForms==2.3.3 && \
    pip install -r requirements.txt

RUN apt-get update && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y --no-install-recommends ./google-chrome-stable_current_amd64.deb && \
    rm -f google-chrome-stable_current_amd64.deb

RUN export CHROMEDRIVER_VERSION=$(curl --silent https://chromedriver.storage.googleapis.com/LATEST_RELEASE_111) && \
    wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/bin && \
    chmod 755 /usr/bin/chromedriver && \
    rm -f chromedriver_linux64.zip

# Configure Filesystem
COPY bin /usr/local/bin
COPY config/superset_config.py /superset_config.py
COPY config/custom_sso_security_manager.py /custom_sso_security_manager.py
VOLUME /etc/superset
VOLUME /home/superset
VOLUME /var/lib/superset

RUN chmod a+x /usr/local/bin/superset-init.sh

# Finalize application
EXPOSE 8088 5555
USER superset
HEALTHCHECK CMD ["curl", "-f", "http://0.0.0.0:8088/health"]
CMD ["/usr/local/bin/superset-init.sh"]