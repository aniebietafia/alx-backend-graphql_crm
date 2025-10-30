import logging
from datetime import datetime
from celery import shared_task
from django.db.models import Sum, Count
from .models import Customer, Order

# Get an instance of a logger
logger = logging.getLogger(__name__)

@shared_task
def generate_crm_report():
    """
    Generates a weekly CRM report and logs it to a file.
    """
    try:
        # 1. Get total number of customers
        customer_count = Customer.objects.count()

        # 2. Get total number of orders and total revenue
        order_data = Order.objects.aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total_amount')
        )

        total_orders = order_data['total_orders'] or 0
        total_revenue = order_data['total_revenue'] or 0.0

        # Format the report string
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_string = (
            f"{timestamp} - Report: "
            f"{customer_count} customers, "
            f"{total_orders} orders, "
            f"{total_revenue:.2f} revenue\n"
        )

        # Log the report to the specified file
        log_file_path = '/tmp/crm_report_log.txt'
        with open(log_file_path, 'a') as f:
            f.write(report_string)

        logger.info(f"Successfully generated and logged CRM report: {report_string.strip()}")

    except Exception as e:
        logger.error(f"Failed to generate CRM report: {e}", exc_info=True)