from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Location, WeatherData
from unittest.mock import patch, MagicMock

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
        mock_weather_data = {
            'main': {
                'temp': 20.0,
                'feels_like': 19.0,
                'humidity': 65,
                'pressure': 1013
            },
            'wind': {'speed': 5.0},
            'weather': [{'description': 'clear sky', 'icon': '01d'}],
            'name': 'Moscow',
            'sys': {'country': 'RU'},
            'coord': {'lat': 55.7558, 'lon': 37.6173}
        }
        mock_get_weather.return_value = mock_weather_data

        response = self.client.get('/api/weather/current/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['temperature'], 20.0)

    @patch('weather.services.WeatherService.get_weather_by_city')
    def test_search_weather(self, mock_get_weather):
        mock_weather_data = {
            'main': {
                'temp': 25.0,
                'feels_like': 24.0,
                'humidity': 60,
                'pressure': 1012
            },
            'wind': {'speed': 4.0},
            'weather': [{'description': 'sunny', 'icon': '01d'}],
            'name': 'London',
            'sys': {'country': 'GB'},
            'coord': {'lat': 51.5074, 'lon': -0.1278}
        }
        mock_get_weather.return_value = mock_weather_data

        response = self.client.get('/api/weather/search/?q=London')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['temperature'], 25.0)

    @patch('weather.services.WeatherService.get_forecast')
    def test_get_forecast(self, mock_get_forecast):
        mock_forecast_data = {
            'list': [
                {
                    'dt': 1609459200,  # 2021-01-01 00:00:00
                    'main': {
                        'temp': 20.0,
                        'feels_like': 19.0,
                        'humidity': 65,
                        'pressure': 1013
                    },
                    'wind': {'speed': 5.0},
                    'weather': [{'description': 'clear sky', 'icon': '01d'}]
                }
            ]
        }
        mock_get_forecast.return_value = mock_forecast_data

        response = self.client.get('/api/weather/forecast/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data, list))

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
        response = self.client.post('/api/locations/set_default/', {
            'location_id': response.data[1]['id']  # ID Парижа
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверка, что Париж стал локацией по умолчанию
        response = self.client.get('/api/locations/')
        self.assertTrue(response.data[1]['is_default'])
