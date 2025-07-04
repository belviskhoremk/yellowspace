from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'product_count', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    readonly_fields = ['created_at', 'product_count']
    prepopulated_fields = {"name": ("name",)}  # optional slug-like behavior

    def product_count(self, obj):
        return obj.product_count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'quantity', 'created_at']
    list_filter = ['category']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
