from django.shortcuts import render

# Create your views here.
def products(request):
    return render(request, 'products.html')


# products/views.py
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
import requests


def product_detail(request, product_id):
    # Get base URL for API requests
    base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash

    # Fetch product details from API
    product_response = requests.get(f"{base_url}/api/products/{product_id}/")
    product = product_response.json() if product_response.status_code == 200 else None

    # Process product images for easier template usage
    if product:
        # Create a list of all available images with their URLs
        product_images = []
        for i in range(1, 6):
            image_url = product.get(f'image_{i}_url')
            if image_url:
                product_images.append({
                    'url': image_url,
                    'alt': f"{product['name']} - Image {i}"
                })

        # Add processed images to product data
        product['product_images'] = product_images
        product['has_images'] = len(product_images) > 0
        product['primary_image'] = product_images[0]['url'] if product_images else None

    # Fetch related products from API (filter by same category)
    category_id = product['category']['id'] if product else None
    related_response = requests.get(
        f"{base_url}/api/products/?category={category_id}&limit=4"
    ) if category_id else None
    related_products = related_response.json()[
        'results'] if related_response and related_response.status_code == 200 else []

    # Process related products images
    for related_product in related_products:
        if related_product.get('primary_image_url'):
            related_product['primary_image'] = related_product['primary_image_url']

    # Fetch reviews for the product
    reviews_response = requests.get(f"{base_url}/api/reviews/?product={product_id}")
    reviews = reviews_response.json()['results'] if reviews_response.status_code == 200 else []

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'cart_count': request.session.get('cart_count', 0)
    }

    return render(request, 'product-detail.html', context)


from rest_framework import generics, status, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Product
from .serializers import (
    ProductSerializer, ProductCreateSerializer, ProductUpdateSerializer,
    ProductListSerializer, ProductStockUpdateSerializer
)


class ProductListAPIView(generics.ListAPIView):
    """
    List all products with filtering and search
    """
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at', 'quantity']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset().select_related('category')

        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            try:
                queryset = queryset.filter(category_id=int(category_id))
            except ValueError:
                pass

        # Filter by category name
        category_name = self.request.query_params.get('category_name')
        if category_name:
            queryset = queryset.filter(category__name__icontains=category_name)

        # Filter by stock availability
        in_stock = self.request.query_params.get('in_stock')
        if in_stock is not None:
            if in_stock.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(quantity__gt=0)
            elif in_stock.lower() in ['false', '0', 'no']:
                queryset = queryset.filter(quantity=0)

        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass

        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass

        # Filter by minimum quantity
        min_quantity = self.request.query_params.get('min_quantity')
        if min_quantity:
            try:
                queryset = queryset.filter(quantity__gte=int(min_quantity))
            except ValueError:
                pass

        # Filter products with images
        has_images = self.request.query_params.get('has_images')
        if has_images is not None:
            if has_images.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(
                    Q(image_1__isnull=False) | Q(image_2__isnull=False) |
                    Q(image_3__isnull=False) | Q(image_4__isnull=False) |
                    Q(image_5__isnull=False)
                )
            elif has_images.lower() in ['false', '0', 'no']:
                queryset = queryset.filter(
                    image_1__isnull=True, image_2__isnull=True,
                    image_3__isnull=True, image_4__isnull=True,
                    image_5__isnull=True
                )

        return queryset


class ProductDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve a specific product
    """
    queryset = Product.objects.all().select_related('category')
    serializer_class = ProductSerializer
    lookup_field = 'id'


class ProductCreateAPIView(generics.CreateAPIView):
    """
    Create a new product
    """
    queryset = Product.objects.all()
    serializer_class = ProductCreateSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        # Return full product details
        response_serializer = ProductSerializer(product, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ProductUpdateAPIView(generics.UpdateAPIView):
    """
    Update a product (full or partial update)
    """
    queryset = Product.objects.all()
    serializer_class = ProductUpdateSerializer
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        # Return full product details
        response_serializer = ProductSerializer(product, context={'request': request})
        return Response(response_serializer.data)


class ProductDeleteAPIView(generics.DestroyAPIView):
    """
    Delete a product
    """
    queryset = Product.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        product_name = instance.name

        # Clean up image files before deletion
        for i in range(1, 6):
            image_field = getattr(instance, f'image_{i}')
            if image_field:
                try:
                    image_field.delete(save=False)
                except Exception:
                    pass  # Continue deletion even if image cleanup fails

        instance.delete()
        return Response({
            'message': f'Product "{product_name}" has been deleted successfully'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
def bulk_upload_images(request, product_id):
    """
    API endpoint to upload multiple images for a product
    """
    try:
        product = get_object_or_404(Product, id=product_id)

        # Get uploaded files
        uploaded_files = []
        for i in range(1, 6):
            file_key = f'image_{i}'
            if file_key in request.FILES:
                uploaded_files.append((i, request.FILES[file_key]))

        if not uploaded_files:
            return Response({
                'error': 'No images provided'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Update product with new images
        for position, image_file in uploaded_files:
            setattr(product, f'image_{position}', image_file)

        product.save()

        # Return updated product data
        serializer = ProductSerializer(product, context={'request': request})
        return Response({
            'message': f'Successfully uploaded {len(uploaded_files)} images',
            'product': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_product_image(request, product_id, image_number):
    """
    API endpoint to delete a specific image from a product
    """
    try:
        product = get_object_or_404(Product, id=product_id)

        if image_number < 1 or image_number > 5:
            return Response({
                'error': 'Invalid image number. Must be between 1 and 5.'
            }, status=status.HTTP_400_BAD_REQUEST)

        image_field = getattr(product, f'image_{image_number}')
        if not image_field:
            return Response({
                'error': f'Image {image_number} does not exist for this product'
            }, status=status.HTTP_404_NOT_FOUND)

        # Delete the image file
        image_field.delete(save=False)
        setattr(product, f'image_{image_number}', None)
        product.save()

        # Return updated product data
        serializer = ProductSerializer(product, context={'request': request})
        return Response({
            'message': f'Image {image_number} deleted successfully',
            'product': serializer.data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
def update_product_stock(request, product_id):
    """
    Update only the stock quantity of a product
    """
    product = get_object_or_404(Product, id=product_id)
    serializer = ProductStockUpdateSerializer(product, data=request.data, partial=True)

    if serializer.is_valid():
        updated_product = serializer.save()
        response_serializer = ProductSerializer(updated_product, context={'request': request})
        return Response({
            'message': f'Stock updated for "{updated_product.name}"',
            'product': response_serializer.data
        })

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def add_stock(request, product_id):
    """
    Add stock to a product
    """
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity_to_add = int(request.data.get('quantity', 0))
        if quantity_to_add <= 0:
            return Response({
                'error': 'Quantity must be greater than 0'
            }, status=status.HTTP_400_BAD_REQUEST)

        product.quantity += quantity_to_add
        product.save()

        serializer = ProductSerializer(product, context={'request': request})
        return Response({
            'message': f'Added {quantity_to_add} units to "{product.name}"',
            'product': serializer.data
        })

    except (ValueError, TypeError):
        return Response({
            'error': 'Invalid quantity value'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def reduce_stock(request, product_id):
    """
    Reduce stock from a product
    """
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity_to_reduce = int(request.data.get('quantity', 0))
        if quantity_to_reduce <= 0:
            return Response({
                'error': 'Quantity must be greater than 0'
            }, status=status.HTTP_400_BAD_REQUEST)

        if product.quantity < quantity_to_reduce:
            return Response({
                'error': f'Not enough stock. Available: {product.quantity}'
            }, status=status.HTTP_400_BAD_REQUEST)

        product.quantity -= quantity_to_reduce
        product.save()

        serializer = ProductSerializer(product, context={'request': request})
        return Response({
            'message': f'Reduced {quantity_to_reduce} units from "{product.name}"',
            'product': serializer.data
        })

    except (ValueError, TypeError):
        return Response({
            'error': 'Invalid quantity value'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def low_stock_products(request):
    """
    Get products with low stock (quantity <= threshold)
    """
    threshold = request.query_params.get('threshold', 10)
    try:
        threshold = int(threshold)
    except ValueError:
        threshold = 10

    low_stock_products = Product.objects.filter(quantity__lte=threshold).select_related('category').order_by('quantity')
    serializer = ProductListSerializer(low_stock_products, many=True, context={'request': request})

    return Response({
        'threshold': threshold,
        'count': low_stock_products.count(),
        'products': serializer.data
    })


@api_view(['GET'])
def product_stats(request):
    """
    Get product statistics
    """
    total_products = Product.objects.count()
    in_stock_products = Product.objects.filter(quantity__gt=0).count()
    out_of_stock_products = Product.objects.filter(quantity=0).count()
    total_inventory_value = sum(p.price * p.quantity for p in Product.objects.all())

    return Response({
        'total_products': total_products,
        'in_stock_products': in_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'total_inventory_value': float(total_inventory_value),
        'stock_rate': round((in_stock_products / total_products * 100), 2) if total_products > 0 else 0
    })


from rest_framework import generics, status, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Category
from .serializers import (
    CategorySerializer, CategoryCreateUpdateSerializer, CategoryListSerializer
)


class CategoryListAPIView(generics.ListAPIView):
    """
    List all categories with filtering
    """
    serializer_class = CategoryListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = Category.objects.all()

        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            if is_active.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(is_active=True)
            elif is_active.lower() in ['false', '0', 'no']:
                queryset = queryset.filter(is_active=False)

        return queryset


class CategoryDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve a specific category with its products
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'


class CategoryCreateAPIView(generics.CreateAPIView):
    """
    Create a new category
    """
    queryset = Category.objects.all()
    serializer_class = CategoryCreateUpdateSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        # Return full category details
        response_serializer = CategorySerializer(category, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CategoryUpdateAPIView(generics.UpdateAPIView):
    """
    Update a category
    """
    queryset = Category.objects.all()
    serializer_class = CategoryCreateUpdateSerializer
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()

        # Return full category details
        response_serializer = CategorySerializer(category, context={'request': request})
        return Response(response_serializer.data)


class CategoryDeleteAPIView(generics.DestroyAPIView):
    """
    Delete a category (only if it has no products)
    """
    queryset = Category.objects.all()
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Check if category has products
        if instance.products.exists():
            return Response({
                'error': f'Cannot delete category "{instance.name}" because it contains {instance.product_count()} products. Please move or delete the products first.'
            }, status=status.HTTP_400_BAD_REQUEST)

        category_name = instance.name
        instance.delete()
        return Response({
            'message': f'Category "{category_name}" has been deleted successfully'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
def category_products(request, category_id):
    """
    Get all products in a specific category
    """
    category = get_object_or_404(Category, id=category_id)
    products = category.products.all()

    # Apply filters similar to product list view
    in_stock = request.query_params.get('in_stock')
    if in_stock is not None:
        if in_stock.lower() in ['true', '1', 'yes']:
            products = products.filter(quantity__gt=0)
        elif in_stock.lower() in ['false', '0', 'no']:
            products = products.filter(quantity=0)

    from .serializers import ProductListSerializer
    serializer = ProductListSerializer(products, many=True, context={'request': request})

    return Response({
        'category': CategorySerializer(category, context={'request': request}).data,
        'products': serializer.data,
        'total_products': products.count()
    })


@api_view(['PATCH'])
def toggle_category_status(request, category_id):
    """
    Toggle category active status
    """
    category = get_object_or_404(Category, id=category_id)
    category.is_active = not category.is_active
    category.save()

    status_text = "activated" if category.is_active else "deactivated"
    serializer = CategorySerializer(category, context={'request': request})

    return Response({
        'message': f'Category "{category.name}" has been {status_text}',
        'category': serializer.data
    })


@api_view(['GET'])
def category_stats(request):
    """
    Get category statistics
    """
    total_categories = Category.objects.count()
    active_categories = Category.objects.filter(is_active=True).count()
    inactive_categories = Category.objects.filter(is_active=False).count()

    # Categories with products
    categories_with_products = Category.objects.filter(products__isnull=False).distinct().count()
    empty_categories = total_categories - categories_with_products

    return Response({
        'total_categories': total_categories,
        'active_categories': active_categories,
        'inactive_categories': inactive_categories,
        'categories_with_products': categories_with_products,
        'empty_categories': empty_categories
    })