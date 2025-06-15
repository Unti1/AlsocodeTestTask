import os
import requests
from django.conf import settings
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHERMAP_API_KEY')
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key is not set")
        self.base_url = "http://api.openweathermap.org/data/2.5"

    def get_current_weather(self, city: str) -> Dict[str, Any]:
        """Получение текущей погоды по названию города"""
        url = f"{self.base_url}/weather"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'ru'
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return self._format_current_weather(response.json())

    def get_weather_by_coordinates(self, lat: str, lon: str) -> Dict[str, Any]:
        """Получение текущей погоды по координатам"""
        url = f"{self.base_url}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'ru'
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return self._format_current_weather(response.json())

    def get_forecast(self, city: str) -> Dict[str, Any]:
        """Получение прогноза погоды на 7 дней"""
        url = f"{self.base_url}/forecast"
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric',
            'lang': 'ru',
            'cnt': 40  # 5 дней * 8 измерений в день
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return self._format_forecast(response.json())

    def _format_current_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Форматирование данных о текущей погоде"""
        return {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': round(data['main']['temp']),
            'feels_like': round(data['main']['feels_like']),
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'wind_speed': data['wind']['speed'],
            'wind_direction': self._get_wind_direction(data['wind']['deg']),
            'sunrise': self._format_time(data['sys']['sunrise']),
            'sunset': self._format_time(data['sys']['sunset']),
            'clouds': data['clouds']['all'],
            'visibility': data.get('visibility', 'Нет данных'),
            'coordinates': {
                'lat': data['coord']['lat'],
                'lon': data['coord']['lon']
            }
        }

    def _format_forecast(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Форматирование данных прогноза погоды"""
        daily_forecasts = {}
        
        for item in data['list']:
            date = item['dt_txt'].split()[0]
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    'date': date,
                    'city': data['city']['name'],
                    'country': data['city']['country'],
                    'temperatures': [],
                    'descriptions': [],
                    'icons': [],
                    'humidity': [],
                    'pressure': [],
                    'wind_speed': [],
                    'clouds': []
                }
            
            forecast = daily_forecasts[date]
            forecast['temperatures'].append(round(item['main']['temp']))
            forecast['descriptions'].append(item['weather'][0]['description'])
            forecast['icons'].append(item['weather'][0]['icon'])
            forecast['humidity'].append(item['main']['humidity'])
            forecast['pressure'].append(item['main']['pressure'])
            forecast['wind_speed'].append(item['wind']['speed'])
            forecast['clouds'].append(item['clouds']['all'])

        # Вычисляем средние значения для каждого дня
        for date, forecast in daily_forecasts.items():
            forecast['avg_temperature'] = round(sum(forecast['temperatures']) / len(forecast['temperatures']))
            forecast['avg_humidity'] = round(sum(forecast['humidity']) / len(forecast['humidity']))
            forecast['avg_pressure'] = round(sum(forecast['pressure']) / len(forecast['pressure']))
            forecast['avg_wind_speed'] = round(sum(forecast['wind_speed']) / len(forecast['wind_speed']), 1)
            forecast['avg_clouds'] = round(sum(forecast['clouds']) / len(forecast['clouds']))
            
            # Выбираем наиболее частое описание погоды
            forecast['description'] = max(set(forecast['descriptions']), key=forecast['descriptions'].count)
            forecast['icon'] = forecast['icons'][0]  # Берем первую иконку дня
            
            # Удаляем списки, оставляем только средние значения
            del forecast['temperatures']
            del forecast['descriptions']
            del forecast['icons']
            del forecast['humidity']
            del forecast['pressure']
            del forecast['wind_speed']
            del forecast['clouds']

        return {
            'city': data['city']['name'],
            'country': data['city']['country'],
            'forecasts': list(daily_forecasts.values())
        }

    def _get_wind_direction(self, degrees: float) -> str:
        """Преобразование градусов в направление ветра"""
        directions = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ']
        index = round(degrees / 45) % 8
        return directions[index]

    def _format_time(self, timestamp: int) -> str:
        """Форматирование времени из timestamp"""
        return datetime.fromtimestamp(timestamp).strftime('%H:%M')

    def process_weather_data(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка данных о погоде в удобный формат"""
        return {
            'temperature': weather_data['main']['temp'],
            'feels_like': weather_data['main']['feels_like'],
            'humidity': weather_data['main']['humidity'],
            'pressure': weather_data['main']['pressure'],
            'wind_speed': weather_data['wind']['speed'],
            'description': weather_data['weather'][0]['description'],
            'icon': weather_data['weather'][0]['icon'],
            'city': weather_data['name'],
            'country': weather_data['sys']['country'],
            'latitude': weather_data['coord']['lat'],
            'longitude': weather_data['coord']['lon'],
        }

    def process_forecast_data(self, forecast_data: Dict[str, Any]) -> list:
        """Обработка данных прогноза погоды"""
        processed_forecast = []
        current_date = None
        daily_forecast = None

        for item in forecast_data['list']:
            date = datetime.fromtimestamp(item['dt']).date()
            
            if current_date != date:
                if daily_forecast:
                    processed_forecast.append(daily_forecast)
                
                current_date = date
                daily_forecast = {
                    'date': date,
                    'temperature': item['main']['temp'],
                    'feels_like': item['main']['feels_like'],
                    'humidity': item['main']['humidity'],
                    'pressure': item['main']['pressure'],
                    'wind_speed': item['wind']['speed'],
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon'],
                }

        if daily_forecast:
            processed_forecast.append(daily_forecast)

        return processed_forecast[:7]  # Возвращаем прогноз на 7 дней 