from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, api_entry_point

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('', api_entry_point, name='api-root'),
    path('', include(router.urls)),
]

