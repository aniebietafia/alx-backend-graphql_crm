import logging
from datetime import datetime
from celery import shared_task
import requests
from decimal import Decimal

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Define the GraphQL query
CRM_REPORT_QUERY = """
query ReportQuery {
  allCustomers {
    totalCount
  }
  allOrders {
    totalCount
    edges {
      node {
        totalAmount
      }
    }
  }
}
"""

# Define the GraphQL endpoint URL.
GRAPHQL_ENDPOINT = 'http://127.0.0.1:8000/graphql'


@shared_task
def generate_crm_report():
    """
    Generates a weekly CRM report by querying the GraphQL endpoint
    and logs the report to a file.
    """
    try:
        # 1. Execute the GraphQL query
        response = requests.post(GRAPHQL_ENDPOINT, json={'query': CRM_REPORT_QUERY})

        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        data = response.json().get('data')

        if not data:
            logger.error(f"GraphQL query failed. Response: {response.json().get('errors')}")
            return

        # 2. Parse the results
        customer_count = data.get('allCustomers', {}).get('totalCount', 0)
        total_orders = data.get('allOrders', {}).get('totalCount', 0)

        # Calculate total revenue from all orders
        # Note: This simple query fetches all orders. For very large datasets,
        # you might want a dedicated 'totalRevenue' field in your schema.
        orders = data.get('allOrders', {}).get('edges', [])
        total_revenue = Decimal('0.0')
        for order in orders:
            if order and order.get('node') and order['node'].get('totalAmount'):
                try:
                    total_revenue += Decimal(order['node']['totalAmount'])
                except (Decimal.InvalidOperation, TypeError):
                    logger.warning(f"Invalid totalAmount skipped: {order['node']['totalAmount']}")

        # 3. Format the report string
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_string = (
            f"{timestamp} - Report: "
            f"{customer_count} customers, "
            f"{total_orders} orders, "
            f"{total_revenue:.2f} revenue\n"
        )

        # 4. Log the report to the specified file
        log_file_path = '/tmp/crm_report_log.txt'
        with open(log_file_path, 'a') as f:
            f.write(report_string)

        logger.info(f"Successfully generated and logged CRM report: {report_string.strip()}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to GraphQL endpoint: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Failed to generate CRM report: {e}", exc_info=True)