import os
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from requests.exceptions import ConnectionError
from gql.transport.exceptions import TransportQueryError

LOG_FILE = "/tmp/crm_heartbeat_log.txt"

GRAPHQL_ENDPOINT = os.environ.get("GRAPHQL_ENDPOINT", "http://127.0.0.1:8000/graphql/")


def log_crm_heartbeat():
    """
    Logs a heartbeat message by executing a live query against the GraphQL endpoint.
    """
    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y-%H:%M:%S")

    gql_status = ""

    try:
        # 1. Set up the transport
        transport = RequestsHTTPTransport(
            url=GRAPHQL_ENDPOINT,
            verify=False,  # Set to True in production with valid SSL
            retries=3,
        )

        # 2. Create the GQL client
        client = Client(transport=transport, fetch_schema_from_transport=False)

        # 3. Define the simple "hello" query
        query = gql("{ hello }")

        # 4. Execute the query
        result = client.execute(query)

        if result and result.get('hello'):
            gql_status = f"GraphQL OK ({result.get('hello')})"
        else:
            gql_status = f"GraphQL query returned unexpected data: {result}"

    except ConnectionError:
        # This error happens if the server is not running
        gql_status = f"GraphQL Error: Connection refused at {GRAPHQL_ENDPOINT} (Server is down)"
    except Exception as e:
        # Catch any other exceptions (e.g., query errors, timeouts)
        gql_status = f"GraphQL Exception: {e}"

    # 5. Format the final log message and append to file
    message = f"{timestamp} CRM is alive. {gql_status}\n"

    try:
        with open(LOG_FILE, "a") as f:
            f.write(message)
    except Exception as e:
        # Fallback if logging to file fails
        print(f"Error writing to {LOG_FILE}: {e}")

LOW_STOCK_LOG_FILE = "/tmp/low_stock_updates_log.txt"


def update_low_stock():
    """
    Executes the UpdateLowStockProducts mutation via GraphQL
    and logs the updated products.
    """
    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y-%H:%M:%S")
    log_messages = [f"--- Cron Job Start: {timestamp} ---"]

    try:
        # 1. Set up transport
        transport = RequestsHTTPTransport(
            url=GRAPHQL_ENDPOINT,
            verify=False,
            retries=3,
        )

        # 2. Create client
        client = Client(transport=transport, fetch_schema_from_transport=False)

        # 3. Define the mutation query
        mutation = gql("""
            mutation UpdateStock {
              updateLowStockProducts {
                products {
                  name
                  stock
                }
                message
              }
            }
        """)

        # 4. Execute the mutation
        result = client.execute(mutation)

        # 5. Process and log the result
        if result and 'updateLowStockProducts' in result:
            data = result['updateLowStockProducts']
            log_messages.append(f"GraphQL OK: {data.get('message')}")

            products = data.get('products', [])
            if products:
                log_messages.append("Updated products:")
                for prod in products:
                    log_messages.append(f"  - Name: {prod.get('name')}, New Stock: {prod.get('stock')}")
            else:
                log_messages.append("No products were updated.")
        else:
            log_messages.append(f"GraphQL query returned unexpected data: {result}")

    except ConnectionError:
        log_messages.append(f"GraphQL Error: Connection refused at {GRAPHQL_ENDPOINT} (Server is down)")
    except TransportQueryError as e:
        # Catches errors from the GraphQL server (e.g., mutation failed)
        log_messages.append(f"GraphQL Query Error: {e}")
    except Exception as e:
        log_messages.append(f"General Exception: {e}")

    log_messages.append(f"--- Cron Job End: {datetime.now().strftime('%d/%m/%Y-%H:%M:%S')} ---")

    # 6. Write all messages to the log file
    try:
        with open(LOW_STOCK_LOG_FILE, "a") as f:
            for line in log_messages:
                f.write(f"{line}\n")
    except Exception as e:
        # Fallback if logging fails
        print(f"Error writing to {LOW_STOCK_LOG_FILE}: {e}")