"""
URL configuration for core app.
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('robots.txt', views.RobotsView.as_view(), name='robots'),
]
