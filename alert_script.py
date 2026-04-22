# alert_script.py (This should be placed outside of your Django project directory for security)

import os
import django
import datetime
from django.core.mail import send_mail

# Set up Django environment (Important: adjust the path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')  # Replace 'your_project_name'
django.setup()

from crm.models import Pedido, Estado  # Replace 'app_name' with your app name
from store.models import Book
from django.db.models import Q


#precio original USD 490
def convert_to_usd():
    # books = Book.objects.filter(price_usd__isnull=True, price_usd=0)
    books = Book.objects.filter(Q(price_usd__isnull=True) | Q(price_usd=0))
    # books = Book.objects.all()
    for book in books:
        print(book.title)
        converted_price = book.price / 515 # valor real convertido

        # rounded_price = round(converted_price)  # redondeo a la unidad
        rounded_price = round(converted_price, 2)

        book.price_usd = rounded_price
        book.save()
        print(f"Precio Actualizado: {book.title} ---> {book.price_usd}")

def send_delivery_alerts():
    """Sends email alerts for Pedidos with approaching delivery dates."""

    today = datetime.date.today()
    # Calculate the date 5 days from now
    alert_date = today + datetime.timedelta(days=2)

    # Find Pedidos where fecha_entrega is within the next 5 days
    pedidos_to_alert = Pedido.objects.filter(
        fecha_entrega__lte=alert_date,
        fecha_entrega__gte=today, # Ensure it's not in the past
    ).exclude(status=Estado.objects.get(id=8))

    for pedido in pedidos_to_alert:
        # Construct the email message
        subject = f"¡Alerta de Entrega de Pedido! - Order ID: {pedido.id}"
        message = f"""
        Estimado Sr. Vargas,

        Este es un recordatorio de que su pedido (ID: {pedido.id}) está programado para ser entregado el {pedido.fecha_entrega}.

        Libro: {pedido.libro}
        Lugar de Recogida: {pedido.ubicacion}

        Por favor, asegúrese de entregar el pedido en la fecha indicada.

        Gracias,
        Su Sistema
        """
        from_email = 'yandivd@gmail.com'  # Replace with your sending email address
        recipient_list = ['yandivd@gmail.com'] # Replace with client email or get from the model: [pedido.client.email]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            print(f"Alert email sent for Pedido ID: {pedido.id}")
        except Exception as e:
            print(f"Error sending email for Pedido ID: {pedido.id}: {e}")

# utils/price_updater.py
import requests
from django.utils import timezone
from django.core.mail import send_mail
import traceback
from io import StringIO
import sys

def send_alerts_updated_prices(details_log=""):
    """Sends email alerts for Books Prices updated with detailed logs."""

    subject = f"¡Alerta de Precios de Libros Actualizados! - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"

    message = f"""
        Estimado Sr. Vargas,

        Este es un reporte detallado de la actualización de precios de libros según la tasa cambiaria de ElToque.

        {'='*60}
        DETALLES DE LA ACTUALIZACIÓN:
        {'='*60}

        {details_log}

        {'='*60}
        Fin del reporte
        {'='*60}

        Este mensaje ha sido generado automáticamente por el sistema.
    """

    from_email = 'yandivd@gmail.com'
    recipient_list = ['yandivd@gmail.com']

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print("Correo enviado exitosamente")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def update_book_prices_from_api():
    """
    Actualiza los precios de los libros basados en la tasa de cambio actual
    Retorna: (success, message, updated_count, details_log)
    """
    # Capturar todos los prints en un buffer
    log_buffer = StringIO()

    # Redirigir prints al buffer
    original_stdout = sys.stdout
    sys.stdout = log_buffer

    try:
        print('='*60)
        print('INICIANDO ACTUALIZACIÓN DE PRECIOS')
        print('='*60)
        print(f'Fecha y hora: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print()

        current_date = timezone.now().strftime('%Y-%m-%d')
        url = f'https://tasas.eltoque.com/v1/trmi?date_to={current_date}%2000%3A00%3A01'

        print(f'URL consultada: {url}')
        print(f'Fecha solicitada: {current_date}')
        print()

        headers = {
            'accept': '*/*',
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2MjI3OTU2MSwianRpIjoiYTU5Yzk1NzYtZDQyMi00Y2ZiLWE0YzQtMjE0MGJjMTBiNjAyIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6IjY5MDkwNWQ5ZTkyYmU3N2VhMzZhM2JlMiIsIm5iZiI6MTc2MjI3OTU2MSwiZXhwIjoxNzkzODE1NTYxfQ.ZS80dOnhco1P5haRQDyAqIBiOSRQsGsZop2O_SvgWXs'
        }

        print('Realizando petición a la API...')
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=30, verify=False)

        print(f'Status Code: {response.status_code}')
        response.raise_for_status()

        data = response.json()
        print(f'Respuesta API: {data}')
        print()

        usd_rate = data['tasas']['USD']
        print(f'TASA DE CAMBIO OBTENIDA: {usd_rate} CUP/USD')
        print()

        books_to_update = Book.objects.filter(price_usd__isnull=False, price_usd__gt=0)
        total_books = books_to_update.count()
        print(f'Total de libros a actualizar: {total_books}')
        print()

        updated_count = 0
        failed_count = 0
        books_details = []

        print('-'*60)
        print('DETALLE DE LIBROS ACTUALIZADOS:')
        print('-'*60)

        for book in books_to_update:
            try:
                old_price = book.price
                new_price = round(book.price_usd * usd_rate) + 500
                book.price = new_price
                book.save()

                book_detail = (f"✓ {book.title}\n"
                              f"  USD: {book.price_usd} | "
                              f"Precio anterior: {old_price} CUP | "
                              f"Nuevo precio: {new_price} CUP")
                books_details.append(book_detail)
                print(book_detail)
                updated_count += 1

            except Exception as e:
                failed_count += 1
                error_detail = f"✗ ERROR al actualizar {book.title}: {str(e)}"
                books_details.append(error_detail)
                print(error_detail)

        print()
        print('-'*60)
        print('RESUMEN FINAL:')
        print('-'*60)
        print(f'✅ Libros actualizados exitosamente: {updated_count}')
        print(f'❌ Libros con error: {failed_count}')
        print(f'📊 Total procesados: {total_books}')
        print()
        print(f'💱 Tasa utilizada: 1 USD = {usd_rate} CUP')
        print(f'➕ Incremento fijo aplicado: 500 CUP')
        print()
        print('='*60)
        print('ACTUALIZACIÓN COMPLETADA')
        print('='*60)

        # Recuperar todo el contenido impreso
        details_log = log_buffer.getvalue()

        # Enviar correo con los detalles
        email_sent = send_alerts_updated_prices(details_log)

        if email_sent:
            print("Reporte enviado por correo electrónico")
        else:
            print("ERROR: No se pudo enviar el correo de reporte")

        # Restaurar stdout
        sys.stdout = original_stdout

        success_message = f"Precios actualizados exitosamente. Tasa: {usd_rate}, Libros actualizados: {updated_count}"
        return True, success_message, updated_count, details_log

    except requests.exceptions.RequestException as e:
        error_log = log_buffer.getvalue()
        error_msg = f'Error en la petición HTTP: {e}'
        print(error_msg)
        traceback.print_exc()

        details_log = f"{error_log}\n\n{'='*60}\nERROR:\n{'='*60}\n{error_msg}\n{traceback.format_exc()}"

        # Enviar correo con el error
        send_alerts_updated_prices(details_log)

        # Restaurar stdout
        sys.stdout = original_stdout

        return False, error_msg, 0, details_log

    except KeyError as e:
        error_log = log_buffer.getvalue()
        error_msg = f'Error en la estructura de la respuesta: {e}'
        print(error_msg)

        details_log = f"{error_log}\n\n{'='*60}\nERROR:\n{'='*60}\n{error_msg}"

        send_alerts_updated_prices(details_log)
        sys.stdout = original_stdout

        return False, error_msg, 0, details_log

    except Exception as e:
        error_log = log_buffer.getvalue()
        error_msg = f'Error inesperado: {str(e)}'
        print(error_msg)
        error_traceback = traceback.format_exc()
        print(f'Traceback: {error_traceback}')

        details_log = f"{error_log}\n\n{'='*60}\nERROR:\n{'='*60}\n{error_msg}\n\n{error_traceback}"

        send_alerts_updated_prices(details_log)
        sys.stdout = original_stdout

        return False, error_msg, 0, details_log
if __name__ == "__main__":
    # send_delivery_alerts()
    # send_alerts_updated_prices()
    convert_to_usd()
    update_book_prices_from_api()
