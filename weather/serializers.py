from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Location, WeatherData

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id',)

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'city', 'country', 'latitude', 'longitude', 'is_default')
        read_only_fields = ('id',)

class WeatherDataSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)

    class Meta:
        model = WeatherData
        fields = ('id', 'location', 'temperature', 'feels_like', 'humidity',
                 'pressure', 'wind_speed', 'description', 'icon', 'timestamp')
        read_only_fields = ('id', 'timestamp') 