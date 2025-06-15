from django.shortcuts import render, redirect
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Location, WeatherData
from .serializers import LocationSerializer, WeatherDataSerializer
from .services import WeatherService
from .forms import CustomUserCreationForm
import requests
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

class LocationViewSet(viewsets.ModelViewSet):
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Location.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        location = self.get_object()
        Location.objects.filter(user=request.user).update(is_default=False)
        location.is_default = True
        location.save()
        return Response({'status': 'default location set'})

class WeatherViewSet(viewsets.ModelViewSet):
    queryset = WeatherData.objects.all()
    serializer_class = WeatherDataSerializer

    @action(detail=False, methods=['get'])
    def current(self, request):
        city = request.query_params.get('city', 'Moscow')
        weather_service = WeatherService()
        weather_data = weather_service.get_current_weather(city)
        return Response(weather_data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        city = request.query_params.get('city')
        if not city:
            return Response({'error': 'City parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        weather_service = WeatherService()
        weather_data = weather_service.get_current_weather(city)
        return Response(weather_data)

    @action(detail=False, methods=['get'])
    def forecast(self, request):
        city = request.query_params.get('city', 'Moscow')
        weather_service = WeatherService()
        forecast_data = weather_service.get_forecast(city)
        return Response(forecast_data)

    @action(detail=False, methods=['get'])
    def by_coordinates(self, request):
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        if not lat or not lon:
            return Response({'error': 'Latitude and longitude are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        weather_service = WeatherService()
        weather_data = weather_service.get_weather_by_coordinates(lat, lon)
        return Response(weather_data)

@login_required
def home(request):
    """Представление для главной страницы"""
    context = {}
    if request.user.is_authenticated:
        try:
            default_location = Location.objects.get(user=request.user, is_default=True)
            weather_service = WeatherService()
            weather_data = weather_service.get_current_weather(default_location.city)
            forecast_data = weather_service.get_forecast(default_location.city)
            
            context['current_weather'] = weather_data
            context['forecast'] = forecast_data['forecasts']
        except Location.DoesNotExist:
            pass
    
    return render(request, 'weather/home.html', context)

@login_required
def forecast_view(request):
    """Представление для страницы прогноза погоды"""
    context = {}
    if request.user.is_authenticated:
        try:
            default_location = Location.objects.get(user=request.user, is_default=True)
            weather_service = WeatherService()
            forecast_data = weather_service.get_forecast(default_location.city)
            context['forecast'] = forecast_data['forecasts']
        except Location.DoesNotExist:
            pass
    
    return render(request, 'weather/forecast.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аккаунт успешно создан! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'weather/register.html', {'form': form})
