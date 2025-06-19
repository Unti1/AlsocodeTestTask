from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

def validate_city(value):
    if not value.isalpha():
        raise ValidationError('Название города должно содержать только буквы')
    if value.isdigit():
        raise ValidationError('Название города не может быть числом')

class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')
    city = models.CharField(max_length=100, validators=[validate_city])
    country = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'city', 'country')

    def __str__(self):
        return f"{self.city}, {self.country}"

class WeatherData(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='weather_data')
    temperature = models.FloatField()
    feels_like = models.FloatField()
    humidity = models.IntegerField()
    pressure = models.IntegerField()
    wind_speed = models.FloatField()
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Weather for {self.location} at {self.timestamp}"
