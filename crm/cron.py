"""
Define a function named log_crm_heartbeat
"""

from datetime import datetime
# Import the schema defined in your project
try:
    from alx_backend_graphql.schema import schema
except ImportError:
    schema = None

LOG_FILE = "/tmp/crm_heartbeat_log.txt"

def log_crm_heartbeat():
    """
    Logs a heartbeat message to a file and optionally queries the GraphQL endpoint.
    """
    # 1. Get current time and format it
    now = datetime.now()
    timestamp = now.strftime("%d/%m/%Y-%H:%M:%S")

    gql_status = "GraphQL schema not loaded."

    # 2. Optionally query the GraphQL 'hello' field
    if schema:
        try:
            # Execute the query
            result = schema.execute('{ hello }')
            if result.errors:
                gql_status = f"GraphQL Error: {result.errors}"
            elif result.data and result.data.get('hello'):
                gql_status = f"GraphQL OK ({result.data.get('hello')})"
            else:
                gql_status = "GraphQL query failed."
        except Exception as e:
            gql_status = f"GraphQL Exception: {e}"

    # 3. Format the final log message
    message = f"{timestamp} CRM is alive. {gql_status}\n"

    # 4. Append to the log file
    try:
        with open(LOG_FILE, "a") as f:
            f.write(message)
    except Exception as e:
        # If logging fails, print to console (will be in cron output)
        print(f"Error writing to {LOG_FILE}: {e}")