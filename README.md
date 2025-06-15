# Weather App

Приложение для просмотра текущей погоды и прогноза на 7 дней с использованием OpenWeatherMap API.

## Требования

- Docker
- Docker Compose
- API ключ OpenWeatherMap

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd weather-app
```

2. Создайте файл .env в корневой директории проекта и добавьте следующие переменные:
```
DEBUG=1
SECRET_KEY=your-secret-key-here
OPENWEATHERMAP_API_KEY=your-api-key-here
POSTGRES_DB=weather_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

3. Запустите приложение с помощью Docker Compose (Poetry сам установит зависимости):
```bash
docker-compose up --build
```

4. Приложение будет доступно по адресу: http://localhost:8000

## API Endpoints

### Текущая погода
- GET /api/weather/current/
- Возвращает текущую погоду для местоположения пользователя

### Поиск погоды
- GET /api/weather/search/?q={city_name}
- Возвращает погоду для указанного города

### Прогноз погоды
- GET /api/weather/forecast/
- Возвращает прогноз погоды на 7 дней

## Тестирование

Для запуска тестов выполните:
```bash
docker-compose run web pytest
```

## Документация API

Документация API доступна по адресу: http://localhost:8000/api/docs/ 