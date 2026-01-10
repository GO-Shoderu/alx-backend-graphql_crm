from datetime import datetime

import requests
from celery import shared_task


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
    url = "http://localhost:8000/graphql"
    query = """
    query {
      allCustomers { id }
      allOrders { id totalAmount }
    }
    """

    try:
        resp = requests.post(url, json={"query": query}, timeout=20)
        resp.raise_for_status()
        data = (resp.json() or {}).get("data") or {}

        customers = data.get("allCustomers") or []
        orders = data.get("allOrders") or []

        customers_count = len(customers)
        orders_count = len(orders)

        revenue = 0.0
        for o in orders:
            val = o.get("totalAmount") or 0
            revenue += float(val)

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{ts} - Report: {customers_count} customers, {orders_count} orders, {revenue} revenue\n"

    except Exception as e:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{ts} - Report: ERROR generating report ({e})\n"

    with open("/tmp/crm_report_log.txt", "a", encoding="utf-8") as f:
        f.write(line)
