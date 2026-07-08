from decimal import Decimal

from rest_framework import serializers

from .models import (
    Customer,
    InventoryMovement,
    Order,
    OrderItem,
    Product,
)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "category",
            "sku",
            "price",
            "stock_quantity",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_price(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError(
                "Price must be greater than zero."
            )
        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Stock quantity cannot be negative."
            )
        return value


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "city",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class OrderSerializer(serializers.ModelSerializer):
    customer_email = serializers.EmailField(
        source="customer.email",
        read_only=True,
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "customer_email",
            "total_amount",
            "status",
            "shipping_address",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_total_amount(self, value):
        if value < Decimal("0.00"):
            raise serializers.ValidationError(
                "Total amount cannot be negative."
            )
        return value


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "order",
            "product",
            "product_name",
            "quantity",
            "unit_price",
        ]
        read_only_fields = ["id"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Quantity must be greater than zero."
            )
        return value

    def validate_unit_price(self, value):
        if value <= Decimal("0.00"):
            raise serializers.ValidationError(
                "Unit price must be greater than zero."
            )
        return value


class InventoryMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True,
    )

    class Meta:
        model = InventoryMovement
        fields = [
            "id",
            "product",
            "product_name",
            "movement_type",
            "quantity",
            "remarks",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_quantity(self, value):
        if value == 0:
            raise serializers.ValidationError(
                "Quantity cannot be zero."
            )
        return value

    def validate_movement_type(self, value):
        valid_types = {"IN", "OUT", "RETURN", "ADJUSTMENT"}

        if value not in valid_types:
            raise serializers.ValidationError(
                f"Movement type must be one of {sorted(valid_types)}."
            )

        return value
