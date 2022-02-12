
name = cms-nft-minting
include .env
export

swagger-gen:
	@swagger-codegen generate -i swagger.yml -l python-flask

build-container:
	@docker build -t genies_nft . --no-cache

up:
	@docker-compose up -d

start:
	@docker-compose start

stop:
	@docker-compose stop

down:
	@docker-compose down

python:
	@docker exec -ti -e COLUMNS=$(shell tput cols) -e LINES=$(shell tput lines) $(shell docker ps --filter name='$(name)-app' --format "{{ .ID }}") python3

ssh:
	@docker exec -ti -e COLUMNS=$(shell tput cols) -e LINES=$(shell tput lines) $(shell docker ps --filter name='$(name)-app' --format "{{ .ID }}") sh

pip:
	@docker exec -ti -e COLUMNS=$(shell tput cols) -e LINES=$(shell tput lines) $(shell docker ps --filter name='$(name)-app' --format "{{ .ID }}") pip3 $(filter-out $@,$(MAKECMDGOALS))

freeze:
	@docker exec -ti -e COLUMNS=$(shell tput cols) -e LINES=$(shell tput lines) $(shell docker ps --filter name='$(name)-app' --format "{{ .ID }}") pip3 freeze > requirements.txt

mysql:
	@docker exec -ti -e COLUMNS=$(shell tput cols) -e LINES=$(shell tput lines) $(shell docker ps --filter name='$(name)-db' --format "{{ .ID }}") mysql -u${DB_USER} -p${DB_PASSWORD} ${DB_SCHEMA} $(filter-out $@,$(MAKECMDGOALS))

test:
	@docker exec -ti -e COLUMNS=$(shell tput cols) -e LINES=$(shell tput lines) $(shell docker ps --filter name='$(name)-app' --format "{{ .ID }}") tox $(filter-out $@,$(MAKECMDGOALS))

black:
	@docker exec -ti -e COLUMNS=$(shell tput cols) -e LINES=$(shell tput lines) $(shell docker ps --filter name='$(name)-app' --format "{{ .ID }}") black $(filter-out $@,$(MAKECMDGOALS))

set-pre-commit:
	@bash scripts/set-pre-commit.sh

sphinx:
	@docker exec -ti -e COLUMNS=$(shell tput cols) -e LINES=$(shell tput lines) $(shell docker ps --filter name='$(name)-app' --format "{{ .ID }}") sh scripts/generate_code_docs.sh

open-docs:
	@open docs/_build/html/index.html

logs:
	@docker-compose logs -f app

migrate:
	@docker exec -ti -e COLUMNS=$(shell tput cols) -e LINES=$(shell tput lines) $(shell docker ps --filter name='$(name)-app' --format "{{ .ID }}") alembic revision --autogenerate -m "$(filter-out $@,$(MAKECMDGOALS))"

merge-migrations:
	@docker exec -ti -e COLUMNS=$(shell tput cols) -e LINES=$(shell tput lines) $(shell docker ps --filter name='$(name)-app' --format "{{ .ID }}") alembic merge heads -m "$(filter-out $@,$(MAKECMDGOALS))"

%:
	@:
