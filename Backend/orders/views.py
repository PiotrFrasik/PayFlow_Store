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

import stripe
from django.conf import settings

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

stripe.api_key = settings.STRIPE_SECRET_KEY

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
        if not product_id:
            return Response({"message": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        cart = RedisCart(request.user.id)
        if cart.remove_item(product_id):
            return Response({"message": "Product removed from cart"})
        return Response({"message": f"Product {product_id} not found in cart"}, status=status.HTTP_404_NOT_FOUND)

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
                # For stripe session
                try:
                    # Round to nearest whole number - converting ZŁ -> GROSZÓWKI  
                    calculated_total_price = int(calculated_total_price*100)
                except ValueError as e:
                    return Response({"message": f"Error processing payment: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

                # Stripe Integration
                session = stripe.checkout.Session.create(
                    payment_method_types = ['card'],
                    mode = 'payment',
                    client_reference_id = str(order.id),
                    success_url = 'http://localhost:8000/success',
                    cancel_url = 'http://localhost:8000/cancel',
                    line_items = [
                        {'price_data': {
                            'currency': 'pln',
                            'product_data': {
                                'name': f"Order #{order.id}",
                            },
                            'unit_amount': calculated_total_price, 
                        },
                        'quantity': 1,}
                    ]
                )

                serializer = OrderSerializer(order)
                return Response(
                    {"order": serializer.data,
                     'checkout_data': session.url},
                     status=status.HTTP_201_CREATED
                    )

            except Product.DoesNotExist:
                return Response({"message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
            except ValueError as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    payload = request.body

    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    if not sig_header:
        return Response({"error": "Missing signature header"}, status=status.HTTP_400_BAD_REQUEST)

    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, 
            sig_header, 
            endpoint_secret
            )
    except ValueError as e:
        # Invalid payload
        return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

    # Handling the successful payment event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Retrieve the order
        order_id = session.client_reference_id
        try:
            order = Order.objects.get(pk=order_id)
            order.status = 'paid'
            order.save()
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    return Response({"success": True}, status=status.HTTP_200_OK)