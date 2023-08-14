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