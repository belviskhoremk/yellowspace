from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'total_price']
    can_delete = False

    def total_price(self, obj):
        return obj.total_price()
    total_price.short_description = "Total (per item)"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'phone_number', 'ordered_at', 'delivered', 'total_price_display']
    list_filter = ['delivered', 'ordered_at']
    search_fields = ['customer_name', 'phone_number', 'email', 'address']
    readonly_fields = ['ordered_at', 'total_price_display']
    inlines = [OrderItemInline]
    actions = ['mark_as_delivered']  # ✅ Reference as a string here

    def total_price_display(self, obj):
        return f"{obj.total_price():.2f} FCFA"
    total_price_display.short_description = "Total Price"

    @admin.action(description="Mark selected orders as delivered")
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(delivered=True)
        self.message_user(request, f"{updated} order(s) marked as delivered.")

