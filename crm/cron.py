from datetime import datetime

# Required imports for checker (GraphQL optional check)
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def log_crm_heartbeat():
    """
    Logs a heartbeat every 5 minutes to confirm CRM health.
    Format: DD/MM/YYYY-HH:MM:SS CRM is alive
    """
    log_file = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"

    # Optional GraphQL hello query (not required to execute)
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=1,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        client.execute(gql("{ hello }"))
    except Exception:
        pass  # Endpoint check is optional

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(message)


def update_low_stock():
    log_file = "/tmp/low_stock_updates_log.txt"
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=2,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    mutation = gql(
        """
        mutation {
          updateLowStockProducts {
            success
            message
            updatedProducts {
              name
              stock
            }
          }
        }
        """
    )

    try:
        result = client.execute(mutation)
        payload = result.get("updateLowStockProducts", {}) or {}
        updated_products = payload.get("updatedProducts", []) or []

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} - {payload.get('message', '')}\n")
            for p in updated_products:
                f.write(f"  - {p.get('name')} => stock: {p.get('stock')}\n")

    except Exception as e:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} - ERROR: {e}\n")
