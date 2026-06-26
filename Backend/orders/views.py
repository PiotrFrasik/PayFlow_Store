from .cart import RedisCart
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import OrderSerializer, OrderItemSerializer
from .models import Order, OrderItem
from products.models import Product
from django.db import transaction
from rest_framework import status

class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = RedisCart(request.user.id)
        items = cart.get_items()
        return Response(items)

    def post(self, request):
        product_id = request.data.get("product_id")
        if not product_id:
            return Response({"message": "Product ID is required"})

        try:
            quantity = int(request.data.get("quantity", 1))
        except ValueError:
            return Response({"message": "Quantity must be an integer"})

        cart = RedisCart(request.user.id)
        cart.add(product_id, quantity)
        return Response({"message": "Product added to cart"})

    def delete(self, request):
        product_id = request.data.get("product_id")
        cart = RedisCart(request.user.id)
        if cart.remove_item(product_id):
            return Response({"message": "Product removed from cart"})
        return Response({"message": "Product not found in cart"})

class OrderCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = RedisCart(request.user.id)
        items = cart.get_items()

        if not items:
            return Response({"message": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            try:
                # Create a base order
                order = Order.objects.create(
                    user=request.user, 
                    status='pending',
                    total_price=0,
                    )

                calculated_total_price = 0

                for product_id, quantity in items.items():
                    # Blocking to prevent race conditions
                    product = Product.objects.select_for_update().get(pk=product_id)

                    # We only check stock for physical products
                    if not product.is_digital:
                        if product.stock_status < quantity:
                            raise ValueError(f"Product {product.name} out of stock")
                        # We subtract from the balance
                        product.stock_status -= quantity
                        product.save()

                    # We create an order item
                    OrderItem.objects.create(
                        order = order,
                        product = product,
                        price = product.price,
                        quantity = quantity
                    )

                    # Calculate the total price
                    calculated_total_price += product.price * quantity

                # Save the total price
                order.total_price = calculated_total_price
                order.save()

                # Clear the cart
                cart.clear()

                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Product.DoesNotExist:
                return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
            except ValueError as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                