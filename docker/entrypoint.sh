#!/bin/sh

echo "Appliquer les migrations..."
python manage.py migrate --noinput

echo "Collecter les fichiers statiques..."
python manage.py collectstatic --noinput

# Lancer Gunicorn pour HTTP
echo "Démarrer Gunicorn pour HTTP..."
gunicorn core.asgi:application --bind 0.0.0.0:8000 --workers 3 --worker-class uvicorn.workers.UvicornWorker &

# Attendre que les deux serveurs terminent (non nécessaire si vous utilisez &)
wait
