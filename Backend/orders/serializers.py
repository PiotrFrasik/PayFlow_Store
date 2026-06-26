from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    totalPrice = serializers.ReadOnlyField(source='get_total_price')
    class Meta:
        model = OrderItem
        fields = ["id", "product", "price", "quantity", "totalPrice"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True,
                                read_only=True)
    
    class Meta:
        model = Order
        fields = ["id", "created_at", "status", "total_price", "items"]
    
    