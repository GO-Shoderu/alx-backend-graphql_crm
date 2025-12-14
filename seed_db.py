import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql.settings")
django.setup()

from crm.models import Customer, Product, Order  # noqa
from django.utils import timezone
from decimal import Decimal


def run():
    # Simple seed – adjust as you like
    alice, _ = Customer.objects.get_or_create(
        email="alice@example.com",
        defaults={"name": "Alice", "phone": "+1234567890"},
    )
    bob, _ = Customer.objects.get_or_create(
        email="bob@example.com",
        defaults={"name": "Bob", "phone": "123-456-7890"},
    )

    laptop, _ = Product.objects.get_or_create(
        name="Laptop",
        defaults={"price": Decimal("999.99"), "stock": 10},
    )
    mouse, _ = Product.objects.get_or_create(
        name="Mouse",
        defaults={"price": Decimal("19.99"), "stock": 50},
    )

    order = Order.objects.create(
        customer=alice,
        total_amount=laptop.price + mouse.price,
        order_date=timezone.now(),
    )
    order.products.set([laptop, mouse])

    print("Seed data created.")


if __name__ == "__main__":
    run()
