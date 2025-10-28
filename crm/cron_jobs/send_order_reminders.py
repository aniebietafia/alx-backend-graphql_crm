#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def send_order_reminders():
    # Calculate date 7 days ago
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    # Setup GraphQL client
    transport = RequestsHTTPTransport(
        url='http://localhost:8000/graphql',
        use_json=True,
    )

    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Define GraphQL query
    query = gql("""
        query GetPendingOrders($startDate: String!) {
            orders(orderDate_Gte: $startDate) {
                id
                orderDate
                customer {
                    email
                }
            }
        }
    """)

    try:
        # Execute query
        result = client.execute(query, variable_values={"startDate": seven_days_ago})

        # Get current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Log reminders
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            for order in result.get('orders', []):
                order_id = order['id']
                customer_email = order['customer']['email']
                log_entry = f"[{timestamp}] Order ID: {order_id}, Customer Email: {customer_email}\n"
                log_file.write(log_entry)

        print("Order reminders processed!")

    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('/tmp/order_reminders_log.txt', 'a') as log_file:
            log_file.write(f"[{timestamp}] ERROR: {str(e)}\n")
        print(f"Error processing reminders: {e}")


if __name__ == "__main__":
    send_order_reminders()
