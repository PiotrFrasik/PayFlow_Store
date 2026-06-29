from celery import shared_task
from django.core.mail import send_mail
from .models import Order

@shared_task
def send_order_confirmation_email(order_id):
    try:
        order = Order.objects.get(pk=order_id)

        subject = f"Confirmed your order #{order.id} - PayFlow Store"
        message = f"Hi {order.user.username}!\n\nThank you for your order.\n\n"
        from_email = "no-reply@payflowstore.com"
        recipient_list = [order.user.email if order.user.email else "test@example.com"]

        send_mail(subject, message, from_email, recipient_list)
        return f"Email sent successfully for order {order_id}"
        
    except Order.DoesNotExist:
        return f"Order {order_id} not found"
