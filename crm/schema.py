import graphene
from graphene_django import DjangoObjectType
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
import re
from .models import Customer, Product, Order


# Object Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'


# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(default_value=0)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# Helper function for phone validation
def validate_phone(phone):
    if phone:
        pattern = r'^\+?\d{1,4}[-.\s]?\(?\d{1,3}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
        if not re.match(pattern, phone):
            raise ValidationError("Invalid phone format")
    return phone


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        try:
            # Validate email
            validate_email(input.email)

            # Check if email already exists
            if Customer.objects.filter(email=input.email).exists():
                raise ValidationError("Email already exists")

            # Validate phone
            validate_phone(input.phone)

            # Create customer instance
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone or ''
            )
            customer.save()

            return CreateCustomer(customer=customer, message="Customer created successfully")

        except ValidationError as e:
            raise Exception(str(e))


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers = []
        errors = []

        with transaction.atomic():
            for idx, customer_data in enumerate(input):
                try:
                    # Validate email
                    validate_email(customer_data.email)

                    # Check if email already exists
                    if Customer.objects.filter(email=customer_data.email).exists():
                        errors.append(f"Customer {idx}: Email already exists - {customer_data.email}")
                        continue

                    # Validate phone
                    validate_phone(customer_data.phone)

                    # Create customer instance
                    customer = Customer(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.phone or ''
                    )
                    customer.save()
                    created_customers.append(customer)

                except ValidationError as e:
                    errors.append(f"Customer {idx}: {str(e)}")
                except Exception as e:
                    errors.append(f"Customer {idx}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        try:
            # Validate price
            if input.price <= 0:
                raise ValidationError("Price must be positive")

            # Validate stock
            if input.stock < 0:
                raise ValidationError("Stock cannot be negative")

            # Create product instance
            product = Product(
                name=input.name,
                price=input.price,
                stock=input.stock
            )
            product.save()

            return CreateProduct(product=product)

        except ValidationError as e:
            raise Exception(str(e))


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            # Validate customer
            try:
                customer = Customer.objects.get(pk=input.customer_id)
            except Customer.DoesNotExist:
                raise ValidationError("Invalid customer ID")

            # Validate products
            if not input.product_ids:
                raise ValidationError("At least one product is required")

            products = []
            total_amount = Decimal('0.00')

            for product_id in input.product_ids:
                try:
                    product = Product.objects.get(pk=product_id)
                    products.append(product)
                    total_amount += product.price
                except Product.DoesNotExist:
                    raise ValidationError(f"Invalid product ID: {product_id}")

            # Create order instance
            order = Order(
                customer=customer,
                order_date=input.order_date,
                total_amount=total_amount
            )
            order.save()

            # Associate products
            order.products.set(products)

            return CreateOrder(order=order)

        except ValidationError as e:
            raise Exception(str(e))


# Query
class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_all_customers(self, info):
        return Customer.objects.all()

    def resolve_all_products(self, info):
        return Product.objects.all()

    def resolve_all_orders(self, info):
        return Order.objects.all()


# Mutation
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
