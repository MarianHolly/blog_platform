FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

# Run migrations, collect static files, and start gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput --clear --verbosity 2 && gunicorn blog_platform.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 60"]