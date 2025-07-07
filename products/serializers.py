from rest_framework import serializers
from .models import Product, Category


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model
    """
    image_url = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'description', 'image', 'image_url',
            'is_active', 'created_at', 'product_count'
        ]
        read_only_fields = ['id', 'created_at', 'image_url', 'product_count']

    def get_image_url(self, obj):
        """Return full URL for the category image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_product_count(self, obj):
        """Return number of products in this category"""
        return obj.product_count()


class CategoryCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating categories
    """
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'is_active']

    def validate_name(self, value):
        """Validate category name uniqueness"""
        instance = getattr(self, 'instance', None)
        if Category.objects.filter(name__iexact=value).exclude(pk=instance.pk if instance else None).exists():
            raise serializers.ValidationError("A category with this name already exists.")
        return value


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for category listings
    """
    image_url = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'image_url', 'is_active', 'product_count']

    def get_image_url(self, obj):
        """Return full URL for the category image"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

    def get_product_count(self, obj):
        """Return number of products in this category"""
        return obj.product_count()


# Updated Product Serializers with Category

class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model with category details
    """
    image_1_url = serializers.SerializerMethodField()
    image_2_url = serializers.SerializerMethodField()
    image_3_url = serializers.SerializerMethodField()
    image_4_url = serializers.SerializerMethodField()
    image_5_url = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    category = CategoryListSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'quantity',
            'image_1', 'image_2', 'image_3', 'image_4', 'image_5',
            'image_1_url', 'image_2_url', 'image_3_url', 'image_4_url', 'image_5_url',
            'images', 'category', 'created_at', 'in_stock'
        ]
        read_only_fields = [
            'id', 'created_at', 'image_1_url', 'image_2_url', 'image_3_url',
            'image_4_url', 'image_5_url', 'images', 'in_stock'
        ]

    def get_image_1_url(self, obj):
        """Return full URL for image_1"""
        if obj.image_1:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_1.url)
            return obj.image_1.url
        return None

    def get_image_2_url(self, obj):
        """Return full URL for image_2"""
        if obj.image_2:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_2.url)
            return obj.image_2.url
        return None

    def get_image_3_url(self, obj):
        """Return full URL for image_3"""
        if obj.image_3:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_3.url)
            return obj.image_3.url
        return None

    def get_image_4_url(self, obj):
        """Return full URL for image_4"""
        if obj.image_4:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_4.url)
            return obj.image_4.url
        return None

    def get_image_5_url(self, obj):
        """Return full URL for image_5"""
        if obj.image_5:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_5.url)
            return obj.image_5.url
        return None

    def get_images(self, obj):
        """Return a list of all image URLs"""
        request = self.context.get('request')
        images = []

        for i in range(1, 6):
            image_field = getattr(obj, f'image_{i}')
            if image_field:
                if request:
                    images.append(request.build_absolute_uri(image_field.url))
                else:
                    images.append(image_field.url)

        return images

    def get_in_stock(self, obj):
        """Check if product is in stock"""
        return obj.quantity > 0


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating products
    """

    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'quantity',
            'image_1', 'image_2', 'image_3', 'image_4', 'image_5',
            'category'
        ]

    def validate_price(self, value):
        """Validate that price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_quantity(self, value):
        """Validate that quantity is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value

    def validate_category(self, value):
        """Validate that category is active"""
        if not value.is_active:
            raise serializers.ValidationError("Cannot add products to inactive categories")
        return value


class ProductUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating products
    """

    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'quantity',
            'image_1', 'image_2', 'image_3', 'image_4', 'image_5',
            'category'
        ]

    def validate_price(self, value):
        """Validate that price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_quantity(self, value):
        """Validate that quantity is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value

    def validate_category(self, value):
        """Validate that category is active"""
        if not value.is_active:
            raise serializers.ValidationError("Cannot move products to inactive categories")
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product listings with category
    """
    primary_image_url = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'quantity', 'primary_image_url',
            'images', 'in_stock', 'category_name'
        ]

    def get_primary_image_url(self, obj):
        """Return the first available image URL"""
        request = self.context.get('request')

        for i in range(1, 6):
            image_field = getattr(obj, f'image_{i}')
            if image_field:
                if request:
                    return request.build_absolute_uri(image_field.url)
                else:
                    return image_field.url

        return None

    def get_images(self, obj):
        """Return a list of all image URLs"""
        request = self.context.get('request')
        images = []

        for i in range(1, 6):
            image_field = getattr(obj, f'image_{i}')
            if image_field:
                if request:
                    images.append(request.build_absolute_uri(image_field.url))
                else:
                    images.append(image_field.url)

        return images

    def get_in_stock(self, obj):
        """Check if product is in stock"""
        return obj.quantity > 0


class ProductStockUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating only product stock
    """

    class Meta:
        model = Product
        fields = ['quantity']

    def validate_quantity(self, value):
        """Validate that quantity is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value