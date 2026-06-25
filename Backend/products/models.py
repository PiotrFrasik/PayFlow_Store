from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100, 
                        unique=True, 
                        blank=False, 
                        null=False)
    description = models.TextField(null=True, 
                                blank=True)
    stock_status = models.PositiveIntegerField(default=0, 
                                null=False, 
                                blank=False)
    price = models.DecimalField(max_digits=10, 
                            decimal_places=2, 
                            null=False, 
                            blank=False)
    is_digital = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.price} = {self.stock_status}"   