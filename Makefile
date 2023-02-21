migrations:
	python manage.py makemigrations
migrate:
	python manage.py migrate
django:
	python manage.py runserver
celery:
	celery -A config.celery_app worker -l info --beat --scheduler django
