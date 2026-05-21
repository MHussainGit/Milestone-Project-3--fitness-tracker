web: gunicorn fittrack.wsgi --workers 2 --timeout 60 --log-file -
release: python manage.py migrate --no-input && python manage.py seed_exercises
