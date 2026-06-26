from .cart import RedisCart
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


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