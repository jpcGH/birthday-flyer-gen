from django.urls import path

from . import views

app_name = 'flyer_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('result/<int:pk>/', views.result, name='result'),
]
