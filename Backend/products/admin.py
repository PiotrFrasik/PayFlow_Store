from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'stock_status', 'is_digital')
    list_filter = ('is_digital', 'stock_status')
    search_fields = ('name',)
