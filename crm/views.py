import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from .models import Pedido, Estado, Book

# Create your views here.
def index(request):
    balance_actual = 0
    pendiente = 0

    for i in Pedido.objects.filter(totalmente_pagado=True):
        balance_actual+=i.libro.price
    for i in Pedido.objects.filter(totalmente_pagado=False):
        balance_actual+=i.pago_anticipado

    for i in Pedido.objects.filter(totalmente_pagado=False):
        pendiente += i.pago_pend

    STATUS_COLORS = {
        'Entregado': 'success',
        'Listo para entregar': 'primary',
        'Pegado': 'warning',
        'Impreso': 'info',
        'Pendiente a impresion': 'danger',
        'Pendiente a portada': 'danger',
        'Pendiente a caratula': 'danger',
        'Pendiente a encuadernacion': 'danger'
    }

    context = {
        'balance_actual': balance_actual,
        'pendiente': pendiente,
        'ventas': Pedido.objects.filter(status = Estado.objects.get(name='Entregado')).count(),
        'total_pedidos': Pedido.objects.all().count(),
        'pedidos': Pedido.objects.exclude(status = Estado.objects.get(name='Entregado')),
        'status_colors': STATUS_COLORS,
        'status': Estado.objects.all(),
        'libros': Book.objects.all()
    }

    if request.method == 'POST':
        new_estado = Estado.objects.get(id=request.POST.get('status'))
        print(new_estado)
        elemento_id = request.POST.get('elemento_id')
        print(elemento_id)

        pedido = Pedido.objects.get(id = elemento_id)
        pedido.status = new_estado

        ### Hacer validaciones para que cuando cambie a entregado se sume el pago pendiente ###
        ### al original y demas cambios que dependen del cambio de estado #####################
        pedido.pago_pend=0
        pedido.totalmente_pagado=True
        pedido.save()

        return redirect('dashboard')
    return render(request, 'dashboard.html', context)

def api_create_pedido(request):
    if request.method == 'POST':
        libro = Book.objects.get(id=request.POST.get('libro')) ##ok
        status = Estado.objects.get(id=1) ##ok
        cliente = request.POST.get('name') ##ok
        telf = request.POST.get('telf') ##ok
        fecha_orden_sol = request.POST.get('fecha_orden')
        print(fecha_orden_sol)
        fecha_orden = datetime.datetime.strptime(fecha_orden_sol, '%Y-%m-%d') ##ok
        print(fecha_orden)
        nueva_fecha = fecha_orden + datetime.timedelta(days=28)
        fecha_entrega = nueva_fecha.strftime('%Y-%m-%d') ##ok
        ubicacion = request.POST.get('ubicacion')
        portada = request.POST.get('portada') ##ok
        if portada == 'on':
            portada = True
        else:
            portada = False

        pago_anticipado = request.POST.get('pago_anticipado') 
        pago_anticipado = int(pago_anticipado)
        pago_pend = request.POST.get('pago_pend')
        pago_pend = int(pago_pend)

        totalmente_pagado = request.POST.get('totalmente_pagado') ##ok
        if totalmente_pagado == 'on':
            totalmente_pagado = True
        else:
            totalmente_pagado = False

        pedido= Pedido.objects.create(libro=libro, status=status, name=cliente, 
                                      telf=telf, fecha_orden=fecha_orden, fecha_entrega=fecha_entrega, 
                                      ubicacion=ubicacion, portada=portada, pago_anticipado=pago_anticipado,
                                      pago_pend=pago_pend, totalmente_pagado=totalmente_pagado)
        #### Hay que tener en cuenta de campos que dependen solo de la creacion del pedido, como estado etc ######
        return JsonResponse({
            'status': 'OK'
        })