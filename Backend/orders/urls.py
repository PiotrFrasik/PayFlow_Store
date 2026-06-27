from django.urls import path
from .views import CartAPIView, OrderCreateAPIView, stripe_webhook

urlpatterns = [
    path('cart/', CartAPIView.as_view(), name='cart'),
    path('create/', OrderCreateAPIView.as_view(), name='create-order'),
    path('webhook/', stripe_webhook, name='stripe-webhook'),
]
