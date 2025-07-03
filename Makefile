.PHONY: build up down clean

build:
	docker build -t myserver ./server
	docker build -t ds-final-project_balancer ./balancer

up: build
	docker-compose up --build -d

down:
	docker-compose down

clean:
	docker system prune -f --volumes
	docker rmi -f myserver ds-final-project_balancer