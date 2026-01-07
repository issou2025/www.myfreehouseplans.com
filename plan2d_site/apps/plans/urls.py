"""
URL configuration for plans app.
"""
from django.urls import path
from . import views

app_name = 'plans'

urlpatterns = [
    path('', views.PlanListView.as_view(), name='list'),
    path('<slug:slug>/', views.PlanDetailView.as_view(), name='detail'),
]
