from django.urls import path
from .views import ProductViewSet
urlpatterns = [
    path('', ProductViewSet.as_view({'get': 'list'}), name='products'),
    path('<int:pk>/', ProductViewSet.as_view({'get': 'retrieve'}), name='product-detail'),
]