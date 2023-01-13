MANAGE_PATH='./backend'
PATH_TO_DOCKER_COMPOSE='./infra'

define find.functions
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'
endef

help: ## вывод доступных команд
	@echo 'The following commands can be used.'
	@echo ''
	$(call find.functions)

setup: ## compose-up mkmigrations migrate suser load-initial-data collecstatic
setup: up mkmigrations migrate suser load static

up: ## docker compose up
up:
	cd $(PATH_TO_DOCKER_COMPOSE); sudo docker compose up -d --build

down: ## docker compose down
down:
	cd $(PATH_TO_DOCKER_COMPOSE); sudo docker compose down -v

mkmigrations: ## makemigrations
mkmigrations:
	cd $(PATH_TO_DOCKER_COMPOSE); sudo docker compose exec web python manage.py makemigrations

migrate: ## migrate
migrate:
	cd $(PATH_TO_DOCKER_COMPOSE); sudo docker compose exec web python manage.py migrate

suser: ## createsuperuser
suser:
	cd $(PATH_TO_DOCKER_COMPOSE); sudo docker compose exec web python manage.py createsuperuser

load: ## load initial data
load:
	cd $(PATH_TO_DOCKER_COMPOSE); sudo docker compose exec web python manage.py load_ingredients_data
	cd $(PATH_TO_DOCKER_COMPOSE); sudo docker compose exec web python manage.py load_tags_data

static: ## collectstatic
static:
	cd $(PATH_TO_DOCKER_COMPOSE); sudo docker compose exec web python manage.py collectstatic --no-input

clean: ## очистить кэш, удалить миграции, удалить бд
clean: rmmigrations rmdb rmcache rmmedia

rmcache: ## очистка кэша
rmcache:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$\)" | xargs rm -rf

rmdb: ## удалить бд
rmdb:
	find . | grep -E db.sqlite3 | xargs rm -f

rmmigrations: ## удалить миграции
rmmigrations:
	find ./backend/ | grep -E 000* | xargs rm -f

rmmedia: ## remove media
rmmedia:
	find ./backend | grep -E media | xargs rm -rf

images: ## docker images
images:
	sudo docker images

cntrls: ## docker container ls -a
cntrls:
	sudo docker container ls -a