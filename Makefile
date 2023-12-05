run:
	echo "Running superset locally with postgres and redis"
	docker-compose up -d

build:
	echo "Building superset locally"
	docker build -f Dockerfile -t superset-local .

build-nocache:
	echo "Building superset locally without cache"
	docker build --no-cache -f Dockerfile -t superset-local .

stop:
	echo "Stopping all containers"
	docker-compose -f docker-compose.yml down -v --remove-orphans


# ----------------------------------------------
# docker / docker-compose targets
# ----------------------------------------------
docker-rebuild-deps:
	docker compose run superset sh -c "\
	pip install pip==23.0.1 && \
	pip install pip-tools==6.12.3 && \
	pip install pip-compile-multi==2.6.3 && \
	pip freeze && \
	pip --version && \
	pip-compile --version && \
	python3 -m pip install -r requirements/integration.txt && pip-compile-multi --no-upgrade --live && \
	find ./requirements -type f -exec sed -i 's|file:///app|file:.|g' {} +"

test:
	@sh -c "echo 1 && \
	echo 2"

docker-build:
	@echo "[$@] Building docker image..."
	docker compose build superset

docker-up:
	docker-compose up superset

docker-shell:
	@echo "[$@] Exec'ing into container..."
	docker exec -it $(shell docker ps | grep superset | awk '{print $$1}') /bin/bash

docker-shell-celery-worker:
	@echo "[$@] Exec'ing into container..."
	docker exec -it $(shell docker ps | grep worker | awk '{print $$1}') /bin/bash
