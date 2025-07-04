from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product
from products.serializers import ProductSerializer
import json

class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for order items with product details
    """
    product = ProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.total_price()


class OrderCreateSerializer(serializers.ModelSerializer):
    items = serializers.CharField(write_only=True)  # Changed to CharField to handle JSON string

    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'phone_number', 'email', 'address',
            'location_lat', 'location_lng', 'ordered_at', 'items', 'notes',
            'paiement_confirmation'
        ]
        read_only_fields = ['id', 'ordered_at']

    def create(self, validated_data):
        items_json = validated_data.pop('items')

        # Parse the JSON string
        try:
            items_data = json.loads(items_json)
        except json.JSONDecodeError:
            raise serializers.ValidationError("Invalid items format")

        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            product_id = item_data.get('product')
            quantity = item_data.get('quantity')

            if not product_id or not quantity:
                continue

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                continue

            if product.quantity < quantity:
                raise serializers.ValidationError(
                    f"Not enough stock for {product.name}. Available: {product.quantity}"
                )

            # Reduce product quantity
            product.quantity -= quantity
            product.save()

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity
            )

        return order

class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving order details with items
    """
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'phone_number', 'email', 'address',
            'location_lat', 'location_lng', 'ordered_at', 'delivered',
            'items', 'total_price', 'notes', 'paiement_confirmation'
        ]

    def get_total_price(self, obj):
        return obj.total_price()


class OrderUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating order information
    """
    class Meta:
        model = Order
        fields = [
            'customer_name', 'phone_number', 'email', 'address',
            'location_lat', 'location_lng', 'delivered', 'notes',
            'paiement_confirmation'
        ]