from datetime import datetime

from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


@shared_task
def generate_crm_report():
    """
    Weekly CRM report:
    - total customers
    - total orders
    - total revenue (sum of totalAmount from orders)
    Logs to: /tmp/crm_report_log.txt
    Format: YYYY-MM-DD HH:MM:SS - Report: X customers, Y orders, Z revenue
    """
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=2,
        timeout=20,
    )
    client = Client(transport=transport, fetch_schema_from_transport=False)

    query = gql(
        """
        query {
          allCustomers { id }
          allOrders { id totalAmount }
        }
        """
    )

    customers_count = 0
    orders_count = 0
    revenue = 0.0

    try:
        result = client.execute(query) or {}

        customers = result.get("allCustomers") or []
        orders = result.get("allOrders") or []

        customers_count = len(customers)
        orders_count = len(orders)

        for o in orders:
            # totalAmount may come as string/float depending on Graphene + Decimal
            val = o.get("totalAmount") or 0
            revenue += float(val)

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{ts} - Report: {customers_count} customers, {orders_count} orders, {revenue} revenue\n"

    except Exception as e:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{ts} - Report: ERROR generating report ({e})\n"

    with open("/tmp/crm_report_log.txt", "a", encoding="utf-8") as f:
        f.write(line)
