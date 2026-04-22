from django.contrib import admin
from .models import Book, Category

# Register your models here.
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'no_pag', 'price','price_usd', 'recomendated','sales_amount')

admin.site.register(Book, BookAdmin)
admin.site.register(Category)
