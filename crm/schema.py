import re
from decimal import Decimal

import graphene
from django.db import transaction
from django.utils import timezone
from graphene_django import DjangoObjectType

from .models import Customer, Product, Order


# =====================
# GraphQL Types
# =====================

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock", "created_at")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


# =====================
# Input Types
# =====================

class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=False)


class OrderInput(graphene.InputObjectType):
    # Graphene will expose these as customerId and productIds in GraphQL
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)


# =====================
# Helper validation
# =====================

PHONE_REGEX = re.compile(r"^(\+?\d{7,15}|\d{3}-\d{3}-\d{4})$")


def validate_phone(phone: str) -> bool:
    if not phone:
        return True
    return bool(PHONE_REGEX.match(phone))


# =====================
# Mutations
# =====================

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input: CustomerInput):
        errors = []

        name = input.name.strip() if input.name else ""
        email = input.email.strip().lower() if input.email else ""
        phone = input.phone.strip() if input.phone else None

        if not name:
            errors.append("Name is required.")
        if not email:
            errors.append("Email is required.")
        elif Customer.objects.filter(email=email).exists():
            errors.append("Email already exists.")
        if phone and not validate_phone(phone):
            errors.append("Invalid phone format. Use +1234567890 or 123-456-7890.")

        if errors:
            return CreateCustomer(
                customer=None,
                message="Failed to create customer.",
                errors=errors,
            )
        
        customer = Customer(
            name=name,
            email=email,
            phone=phone,
        )
        customer.save()

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(
            customer=customer,
            message="Customer created successfully.",
            errors=[],
        )


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    @transaction.atomic
    def mutate(root, info, input):
        created_customers = []
        errors = []

        for index, cust_input in enumerate(input):
            row_prefix = f"Row {index + 1}: "

            name = (cust_input.name or "").strip()
            email = (cust_input.email or "").strip().lower()
            phone = cust_input.phone.strip() if cust_input.phone else None

            row_errors = []
            if not name:
                row_errors.append("Name is required.")
            if not email:
                row_errors.append("Email is required.")
            elif Customer.objects.filter(email=email).exists():
                row_errors.append("Email already exists.")
            if phone and not validate_phone(phone):
                row_errors.append("Invalid phone format.")

            if row_errors:
                errors.append(row_prefix + "; ".join(row_errors))
                continue

            customer = Customer.objects.create(name=name, email=email, phone=phone)
            created_customers.append(customer)

        # Partial success: we return what we could create plus errors
        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input: ProductInput):
        errors = []

        name = (input.name or "").strip()
        price = Decimal(str(input.price)) if input.price is not None else None
        stock = input.stock if input.stock is not None else 0

        if not name:
            errors.append("Name is required.")
        if price is None or price <= 0:
            errors.append("Price must be a positive value.")
        if stock < 0:
            errors.append("Stock cannot be negative.")

        if errors:
            return CreateProduct(product=None, errors=errors)

        product = Product.objects.create(
            name=name,
            price=price,
            stock=stock,
        )
        return CreateProduct(product=product, errors=[])


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    @staticmethod
    @transaction.atomic
    def mutate(root, info, input: OrderInput):
        errors = []

        customer_id = input.customer_id
        product_ids = input.product_ids or []
        order_date = input.order_date or timezone.now()

        # Validate customer
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID.")
            return CreateOrder(order=None, errors=errors)

        # Validate products
        if not product_ids:
            errors.append("At least one product must be selected.")
            return CreateOrder(order=None, errors=errors)

        products = list(Product.objects.filter(pk__in=product_ids))
        if len(products) != len(set(product_ids)):
            errors.append("One or more product IDs are invalid.")
            return CreateOrder(order=None, errors=errors)

        # Calculate total_amount
        total_amount = sum((p.price for p in products), Decimal("0.00"))

        # Create order and associate products
        order = Order.objects.create(
            customer=customer,
            total_amount=total_amount,
            order_date=order_date,
        )
        order.products.set(products)

        return CreateOrder(order=order, errors=[])


# =====================
# Query
# (can be extended in later tasks)
# =====================

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    @staticmethod
    def resolve_all_customers(root, info):
        return Customer.objects.all()

    @staticmethod
    def resolve_all_products(root, info):
        return Product.objects.all()

    @staticmethod
    def resolve_all_orders(root, info):
        return Order.objects.select_related("customer").prefetch_related("products")


# =====================
# Root Mutation
# =====================

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
