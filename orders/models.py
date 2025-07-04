from django.db import models
from products.models import Product

class Order(models.Model):
    customer_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField()
    location_lat = models.FloatField(blank=True, null=True)
    location_lng = models.FloatField(blank=True, null=True)
    ordered_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    paiement_confirmation = models.ImageField(
        upload_to='payment_receipts/',
        blank=True,
        null=True,
        help_text="Upload payment receipt image"
    )

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def total_price(self):
        return self.product.price * self.quantity