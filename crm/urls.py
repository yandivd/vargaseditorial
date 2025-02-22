from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='dashboard'),
    path('api_create_pedido/', api_create_pedido, name='api_create_pedido'),
    path('ver-comprobante/<int:id>/', ver_comprobante, name='ver_comprobantes'),
    path('ver-label/<int:id>/', ver_label, name='ver_label'),
    path('generate-pdf/<int:id>/', generate_pdf, name='generate_pdf'),
    path('generate-label/<int:id>/', generate_label, name='generate_label'),
    path('pedidos_list/', pedidos_list, name='pedidos_list'),
    path('books_list/', book_list, name='books_list'),

]