from django.db import models
from products.models import Product
from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20,
                             choices=[
                                 ('pending', 'Pending'),
                                 ('paid', 'Paid'),
                                 ('failed', 'Failed'),
                             ])
    total_price = models.DecimalField(max_digits=10, 
                                     decimal_places=2,
                                     null=True,
                                     blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, 
                            on_delete=models.CASCADE,
                            related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1, 
                                          null=False, 
                                          blank=False)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} (Order: {self.order.id})"

    def get_total_price(self):
        return self.price * self.quantity