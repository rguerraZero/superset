run:
	echo "Running superset locally with postgres and redis"
	docker-compose up -d redis postgres superset worker flower beat

build:
	echo "Building superset locally"
	docker build -f Docker/Dockerfile.local -t superset .

build-nocache:
	echo "Building superset locally without cache"
	docker build --no-cache -f Docker/Dockerfile.local -t superset .

stop:
	echo "Stopping all containers"
	docker-compose -f docker-compose.yml down -v --remove-orphans