web: gunicorn config.wsgi:application
worker: celery worker --app=stratum.taskapp --loglevel=info
