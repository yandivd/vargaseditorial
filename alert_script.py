# alert_script.py (This should be placed outside of your Django project directory for security)

import os
import django
import datetime
from django.core.mail import send_mail

# Set up Django environment (Important: adjust the path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')  # Replace 'your_project_name'
django.setup()

from crm.models import Pedido, Estado  # Replace 'app_name' with your app name

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

if __name__ == "__main__":
    send_delivery_alerts()
