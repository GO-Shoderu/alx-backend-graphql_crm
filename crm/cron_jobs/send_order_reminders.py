#!/usr/bin/env python3
from datetime import datetime, timedelta, timezone as dt_timezone
import os

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


GRAPHQL_URL = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/order_reminders_log.txt"


def _iso_now() -> str:
    return datetime.now(dt_timezone.utc).strftime("%Y-%m-%d %H:%M:%S%z")


def _parse_dt(value: str) -> datetime | None:
    """
    Best-effort ISO datetime parsing.
    Accepts formats like:
      - 2026-01-05
      - 2026-01-05T12:34:56Z
      - 2026-01-05T12:34:56+00:00
    """
    if not value:
        return None

    try:
        # Normalize 'Z' (Zulu time) to +00:00 for fromisoformat
        value = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=dt_timezone.utc)
        return dt
    except Exception:
        return None


def main() -> None:
    since_dt = datetime.now(dt_timezone.utc) - timedelta(days=7)
    since_iso = since_dt.isoformat()

    transport = RequestsHTTPTransport(
        url=GRAPHQL_URL,
        verify=True,
        retries=3,
        timeout=20,
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    # Attempt 1: server-side filtering (if your schema supports it)
    query_with_filter = gql(
        """
        query GetRecentOrders($since: DateTime!) {
          orders(orderDate_Gte: $since) {
            id
            orderDate
            customer { email }
          }
        }
        """
    )

    # Fallback: fetch orders and filter client-side (if schema doesn’t support args)
    query_no_filter = gql(
        """
        query GetOrders {
          orders {
            id
            orderDate
            customer { email }
          }
        }
        """
    )

    try:
        result = client.execute(query_with_filter, variable_values={"since": since_iso})
        orders = result.get("orders", []) or []
    except Exception:
        # If the schema doesn't support orderDate_Gte (very possible),
        # still satisfy the task by querying via gql, then filtering locally.
        result = client.execute(query_no_filter)
        orders = result.get("orders", []) or []

    # Filter locally to ensure "within last 7 days" logic is respected
    recent = []
    for o in orders:
        order_date = o.get("orderDate")
        dt = _parse_dt(order_date)
        if dt and dt >= since_dt:
            recent.append(o)

    # Log each order’s ID and customer email with timestamp
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for o in recent:
            order_id = o.get("id")
            email = (o.get("customer") or {}).get("email")
            f.write(f"{_iso_now()} - Order ID: {order_id}, Customer Email: {email}\n")

    print("Order reminders processed!")


if __name__ == "__main__":
    main()
