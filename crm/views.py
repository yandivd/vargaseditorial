import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from .models import Pedido, Estado, Book
from django.contrib.auth.decorators import login_required

# Create your views here.

def format_id(id):
    if len(str(id)) == 1:
        return f"00{id}"
    elif len(str(id)) == 2:
        return f"0{id}"
    else:
        return str(id)


@login_required
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
        'libros': Book.objects.all(),
        'nuevos_pedidos': Pedido.objects.filter(status=Estado.objects.get(id=1)).count(),
        'encuadernando': Pedido.objects.filter(status=Estado.objects.get(id=4)).count()+Pedido.objects.filter(status=Estado.objects.get(id=5)).count(),
        'listos_entregar': Pedido.objects.filter(status=Estado.objects.get(id=7)).count()
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
        if new_estado == Estado.objects.get(id=8):
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

        libro.sales_amount=libro.sales_amount+1
        libro.save()
        pedido= Pedido.objects.create(libro=libro, status=status, name=cliente, 
                                      telf=telf, fecha_orden=fecha_orden, fecha_entrega=fecha_entrega, 
                                      ubicacion=ubicacion, portada=portada, pago_anticipado=pago_anticipado,
                                      pago_pend=pago_pend, totalmente_pagado=totalmente_pagado)
        #### Hay que tener en cuenta de campos que dependen solo de la creacion del pedido, como estado etc ######
        return JsonResponse({
            'status': 'OK'
        })
    
def ver_comprobante(request, id):
    
    try:
        # Asumiendo que tienes una vista con acceso al id o pk
        # Cambia esto según tus necesidades.
        
        # Obtén el objeto Pedido usando su ID o PK.
        # Reemplaza 'pk' por cualquier otro parámetro que uses para identificarlo.
        comprobante = Pedido.objects.get(id=id)
        print(comprobante)
        return render(request, 'invoice.html', {'pedido': comprobante})
    
    except Exception as e:
        print(f"Error al obtener el comprobante {e}")
        return HttpResponse("Error al cargar datos.")
    
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.templatetags.static import static

def generate_pdf(request, id):
    # 1. Renderiza el template HTML.
    try:
        # Asumiendo que tienes una vista con acceso al id o pk
        # Cambia esto según tus necesidades.
        
        # Obtén el objeto Pedido usando su ID o PK.
        # Reemplaza 'pk' por cualquier otro parámetro que uses para identificarlo.
        comprobante = Pedido.objects.get(id=id)
    except Exception as e:
        print(e)
        

    template = get_template('invoice.html') # Reemplaza 'mi_template.html' con el nombre de tu template.
    context = {
        'titulo': 'Mi Documento PDF',
        'contenido': 'Este es el contenido generado desde el template.',
        'logo_url': static('img/logo.png'),  # Ruta al logo (LOCAL)
        'qr_code_url': static('img/qr.jpeg'),  # Ruta al código QR
        'pedido': comprobante
        # ... otros datos que necesitas pasar a tu template
    }
    html = template.render(context)

    # 2. Crea un objeto BytesIO para guardar el PDF.
    buffer = BytesIO()

    # 3. Convierte el HTML a PDF usando xhtml2pdf.
    pisa_status = pisa.CreatePDF(
        html,                # El HTML a convertir
        dest=buffer           # El buffer donde guardar el PDF
    )

    # Si hubo un error, lo puedes manejar aquí.
    if pisa_status.err:
        return HttpResponse('Error al generar el PDF: <pre>' + html + '</pre>')

    # 4. Regresa la respuesta HTTP con el PDF.
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="documento.pdf"'
    return response

def pedidos_list(request):
    pedidos=Pedido.objects.all()
    return render(request, 'pedidos_list.html', {
        'pedidos':pedidos
    })

def book_list(request):
    books=Book.objects.all()
    return render(request, 'book_list.html', {
        'books':books
    })

