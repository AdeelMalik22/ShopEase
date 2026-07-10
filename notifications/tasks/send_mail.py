

from notifications.celery_client import celery

from apps.orders.models import Order
from apps.orders.emails import send_order_confirmation_email


@celery.task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def send_order_confirmation_email_task(order_id):

    order = Order.objects.get(id=order_id)

    send_order_confirmation_email(order)