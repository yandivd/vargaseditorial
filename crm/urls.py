from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='dashboard'),
    path('api_create_pedido/', api_create_pedido, name='api_create_pedido'),
    path('ver-comprobante/<int:id>/', ver_comprobante, name='ver_comprobantes'),
]