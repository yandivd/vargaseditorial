from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('tienda/', tienda, name='tienda'),
    path('api/books/', api_books),
    path('book/<int:id>/', book_detail, name='book_detail'),
    path('api_book_detail/<int:id>/', get_book_price),
]