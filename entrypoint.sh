#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! python -c "import socket; s = socket.socket(); s.settimeout(1); s.connect(('$SQL_HOST', ${SQL_PORT:-5432})); s.close()" 2>/dev/null; do
      sleep 0.5
    done

    echo "PostgreSQL started"
fi

[ -d ./allstaticfiles/static ] || mkdir -p ./allstaticfiles/static
[ -d ./media ] || mkdir -p ./media

python manage.py makemigrations --noinput --merge
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py compilemessages

exec "$@"
