from rest_framework import viewsets
from rest_framework.decorators import api_view
from .models import Product
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.reverse import reverse

@api_view(['GET'])
def api_entry_point(request, format=None):
    """
    Main entry point for the REST API.
    """
    return Response({
        'Project description': 'Co moge tutaj napisac?.',
        'Products': reverse('product-list', request=request, format=format),
    })

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
