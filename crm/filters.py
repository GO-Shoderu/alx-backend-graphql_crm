import django_filters
from .models import Customer, Product, Order


class CustomerFilter(django_filters.FilterSet):
    # Custom phone pattern filter – e.g. value = "+1"
    phone_pattern = django_filters.CharFilter(method="filter_phone_pattern")

    # Challenge: order_by support (GraphQL arg will be orderBy)
    order_by = django_filters.OrderingFilter(
        fields=(
            ("name", "name"),
            ("email", "email"),
            ("created_at", "created_at"),
        )
    )

    class Meta:
        model = Customer
        # This style generates GraphQL fields like:
        # nameIcontains, emailIcontains, createdAtGte, createdAtLte
        fields = {
            "name": ["icontains"],
            "email": ["icontains"],
            "created_at": ["gte", "lte"],
        }

    def filter_phone_pattern(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(phone__startswith=value)


class ProductFilter(django_filters.FilterSet):
    # For sorting by name, price, or stock
    order_by = django_filters.OrderingFilter(
        fields=(
            ("name", "name"),
            ("price", "price"),
            ("stock", "stock"),
        )
    )

    class Meta:
        model = Product
        # GraphQL: nameIcontains, priceGte, priceLte, stockGte, stockLte
        fields = {
            "name": ["icontains"],
            "price": ["gte", "lte"],
            "stock": ["gte", "lte"],
        }


class OrderFilter(django_filters.FilterSet):
    # Filter by customer’s name
    customer_name = django_filters.CharFilter(
        field_name="customer__name", lookup_expr="icontains"
    )
    # Filter by product name
    product_name = django_filters.CharFilter(
        field_name="products__name", lookup_expr="icontains"
    )
    # Challenge: Order includes a specific product ID
    product_id = django_filters.NumberFilter(field_name="products__id")

    # Sorting by total_amount or order_date
    order_by = django_filters.OrderingFilter(
        fields=(
            ("order_date", "order_date"),
            ("total_amount", "total_amount"),
        )
    )

    class Meta:
        model = Order
        # GraphQL: totalAmountGte, totalAmountLte, orderDateGte, orderDateLte
        fields = {
            "total_amount": ["gte", "lte"],
            "order_date": ["gte", "lte"],
        }
