import logging
from celery import shared_task
from django.core.mail import send_mail
from .models import Order

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_backoff_max=600, max_retries=3)
def send_order_confirmation_email(self, order_id):
    try:
        order = Order.objects.get(pk=order_id)

        subject = f"Confirmed your order #{order.id} - PayFlow Store"
        message = f"Hi {order.user.username}!\n\nThank you for your order.\n\n"
        from_email = "no-reply@payflowstore.com"
        recipient_list = [order.user.email if order.user.email else "test@example.com"]

        send_mail(subject, message, from_email, recipient_list)
        logger.info("Email sent successfully", extra={"order_id": order_id, "user": order.user.username})
        return f"Email sent successfully for order {order_id}"
        
    except Order.DoesNotExist:
        logger.error("Order not found during email sending", extra={"order_id": order_id})
        # We don't retry if order doesn't exist
        return f"Order {order_id} not found"
    except Exception as exc:
        logger.warning("Failed to send email, retrying...", extra={"order_id": order_id, "error": str(exc)})
        raise exc
