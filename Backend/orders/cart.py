from django.core.cache import cache

class RedisCart():
    def __init__(self, user_id):
        self.user_id = user_id
        # Unique key for RedisDB
        self.cart_key = f"cart:{self.user_id}"

    def add(self, product_id, quantity=1):
        """
        Adds a product to the cart or increases its quantity if it already exists.
        """
        cart = cache.get(self.cart_key) or {}
        product_id_str = str(product_id)

        # Update the basket in Python memory
        if product_id_str in cart:
            cart[product_id_str] += quantity
        else:
            cart[product_id_str] = quantity

        # Save to Redis (expires in 24 hours)
        cache.set(self.cart_key, cart, 86400)

    def get_items(self):
        """
        Returns the entire cart with product IDs and quantities
        """
        return cache.get(self.cart_key) or {}

    def clear(self):
        """
        Clears the entire cart
        """
        cache.delete(self.cart_key)

    def remove_item(self, product_id):
        """
        Removes a specific product from the cart
        """
        cart = cache.get(self.cart_key) or {}
        product_id_str = str(product_id)

        if product_id_str in cart:
            del cart[product_id_str]
            cache.set(self.cart_key, cart, 86400)
            return True
        return False