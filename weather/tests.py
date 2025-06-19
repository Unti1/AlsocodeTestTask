from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Location
from unittest.mock import patch

class WeatherAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.location = Location.objects.create(
            user=self.user,
            city='Moscow',
            country='RU',
            latitude=55.7558,
            longitude=37.6173,
            is_default=True
        )

    @patch('weather.services.WeatherService.get_current_weather')
    def test_get_current_weather(self, mock_get_weather):
        mock_get_weather.return_value = {
            'city': 'Moscow',
            'country': 'RU',
            'temperature': 20,
            'feels_like': 19,
            'description': 'ясно',
            'icon': '01d',
            'humidity': 65,
            'pressure': 1013,
            'wind_speed': 5.0,
            'wind_direction': 'С',
            'sunrise': '06:00',
            'sunset': '18:00',
            'clouds': 0,
            'visibility': 10000,
            'coordinates': {'lat': 55.7558, 'lon': 37.6173},
        }
        response = self.client.get('/api/weather/current/?city=Moscow')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['city'], 'Moscow')

    @patch('weather.services.WeatherService.get_current_weather')
    @patch('weather.services.WeatherService.validate_city_name')
    def test_search_weather(self, mock_validate, mock_get_weather):
        mock_validate.return_value = True
        mock_get_weather.return_value = {
            'city': 'London',
            'country': 'GB',
            'temperature': 25,
            'feels_like': 24,
            'description': 'sunny',
            'icon': '01d',
            'humidity': 60,
            'pressure': 1012,
            'wind_speed': 4.0,
            'wind_direction': 'С',
            'sunrise': '06:00',
            'sunset': '18:00',
            'clouds': 10,
            'visibility': 10000,
            'coordinates': {'lat': 51.5074, 'lon': -0.1278},
        }
        response = self.client.get('/api/weather/search/?q=London')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['city'], 'London')

    @patch('weather.services.WeatherService.get_forecast')
    def test_get_forecast(self, mock_get_forecast):
        mock_get_forecast.return_value = {
            'city': 'Moscow',
            'country': 'RU',
            'forecasts': [
                {
                    'date': '2025-06-20',
                    'city': 'Moscow',
                    'country': 'RU',
                    'avg_temperature': 20,
                    'avg_humidity': 65,
                    'avg_pressure': 1013,
                    'avg_wind_speed': 5.0,
                    'avg_clouds': 0,
                    'description': 'ясно',
                    'icon': '01d',
                }
            ]
        }
        response = self.client.get('/api/weather/forecast/?city=Moscow')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('forecasts', response.data)

    @patch('weather.services.WeatherService.get_weather_by_coordinates')
    def test_by_coordinates(self, mock_get_weather):
        mock_get_weather.return_value = {
            'city': 'Moscow',
            'country': 'RU',
            'temperature': 20,
            'feels_like': 19,
            'description': 'ясно',
            'icon': '01d',
            'humidity': 65,
            'pressure': 1013,
            'wind_speed': 5.0,
            'wind_direction': 'С',
            'sunrise': '06:00',
            'sunset': '18:00',
            'clouds': 0,
            'visibility': 10000,
            'coordinates': {'lat': 55.7558, 'lon': 37.6173},
        }
        response = self.client.get('/api/weather/by_coordinates/?lat=55.7558&lon=37.6173')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['city'], 'Moscow')

    def test_location_management(self):
        # Создание новой локации
        response = self.client.post('/api/locations/', {
            'city': 'Paris',
            'country': 'FR',
            'latitude': 48.8566,
            'longitude': 2.3522
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Получение списка локаций
        response = self.client.get('/api/locations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Москва + Париж

        # Установка локации по умолчанию
        location_id = response.data[1]['id']
        response = self.client.post(f'/api/locations/{location_id}/set_default/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверка, что Париж стал локацией по умолчанию
        response = self.client.get('/api/locations/')
        self.assertTrue(response.data[1]['is_default'])
