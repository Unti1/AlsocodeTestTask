FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY req.txt ./


# Устанавливаем зависимости напрямую через pip
RUN pip install -r req.txt

# Копируем код проекта
COPY . .

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Запускаем приложение
CMD ["/bin/sh", "-c", "python manage.py migrate && python manage.py test weather.tests && python manage.py runserver 0.0.0.0:8000"] 