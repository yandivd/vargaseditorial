from django.db import models
from store.models import Book
from django.utils.safestring import mark_safe

# Create your models here.
class Estado(models.Model):
    name = models.CharField(max_length=50, verbose_name='Nombre')
    color = models.CharField(max_length=7, verbose_name='Color', help_text='Ingrese el color en formato hexadecimal (por ejemplo, #FF0000)')

    def __str__(self):
        return self.name

    def colored_name(self):
        return mark_safe(f'<span style="color: {self.color}">{self.name}</span>')

    colored_name.allow_tags = True
    colored_name.short_description = 'Nombre'

class Agente(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True)
    code = models.CharField(max_length=8)
    saldo = models.IntegerField(default=0)
    def __str__(self):
        return self.code

class Pedido(models.Model):
    libro = models.ForeignKey(Book, verbose_name='Libro', on_delete=models.CASCADE)
    status = models.ForeignKey(Estado, verbose_name='Estado del Pedido', on_delete=models.CASCADE)
    name = models.CharField(max_length=150, verbose_name='Cliente')
    telf = models.CharField(max_length=8, verbose_name='Numero de Telefono')
    fecha_orden = models.DateField(verbose_name='Fecha de Orden')
    fecha_entrega = models.DateField(verbose_name='Fecha de Recogida')
    ubicacion = models.CharField(max_length=150, verbose_name='Lugar de Recogida')
    portada = models.BooleanField(verbose_name='Portada')
    pago_anticipado = models.IntegerField(default=0, verbose_name='Pago Anticipado')
    pago_pend = models.IntegerField(default=0, verbose_name='Pago Pendiente')
    totalmente_pagado = models.BooleanField(default=False, verbose_name='Totalmente Pago')
    code_ref = models.ForeignKey(Agente, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name + ''+self.libro.title

    def colored_status(self):
        return self.status.colored_name()
    
    colored_status.short_description = 'Estado del Pedido'