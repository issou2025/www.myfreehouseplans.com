"""
URL configuration for orders app.
"""
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/<slug:plan_slug>/', views.CheckoutView.as_view(), name='checkout'),
    path('confirmation/<str:order_number>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    path('my-orders/', views.MyOrdersView.as_view(), name='my_orders'),
]
