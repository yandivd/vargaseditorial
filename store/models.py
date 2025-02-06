from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Book(models.Model):
    img = models.ImageField(upload_to='books', verbose_name='Imagen')
    discount = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name='Descuento en %')
    title = models.CharField(max_length=100, verbose_name='Nombre')
    author = models.CharField(max_length=100, verbose_name='Autor')
    category = models.ManyToManyField(Category, verbose_name='Categorías')
    no_pag = models.IntegerField(default=1, verbose_name='Numero de Paginas')
    desc = models.TextField(verbose_name='Descripcion')
    price = models.IntegerField(verbose_name='Precio')
    sales_amount = models.IntegerField(default=0, verbose_name='Cantidad vendida')
    date_added = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de agregado')
    recomendated = models.BooleanField(default=False, verbose_name='Recomendado')
    valoration = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ], default=5
    )
    existencia = models.BooleanField(default=True)

    def discounted_price(self):
        if self.discount is not None and self.price > 0:
            return round(self.price * (1 - (self.discount / 100)))  # Calcula el precio después del descuento
        return self.price  # Retorna el precio original si no hay descuento

    def __str__(self):
        return self.title
