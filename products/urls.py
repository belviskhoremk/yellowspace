from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Product CRUD operations
    path('', views.ProductListAPIView.as_view(), name='product-list'),
    path('create/', views.ProductCreateAPIView.as_view(), name='product-create'),
    path('<int:id>/', views.ProductDetailAPIView.as_view(), name='product-detail'),
    path('<int:id>/update/', views.ProductUpdateAPIView.as_view(), name='product-update'),
    path('<int:id>/delete/', views.ProductDeleteAPIView.as_view(), name='product-delete'),

    # Stock management
    path('<int:product_id>/stock/update/', views.update_product_stock, name='update-stock'),
    path('<int:product_id>/stock/add/', views.add_stock, name='add-stock'),
    path('<int:product_id>/stock/reduce/', views.reduce_stock, name='reduce-stock'),

    # Product analytics and utilities
    path('low-stock/', views.low_stock_products, name='low-stock'),
    path('stats/', views.product_stats, name='product-stats'),

    # Category APIs
    path('categories/', views.CategoryListAPIView.as_view(), name='category-list'),
    path('categories/create/', views.CategoryCreateAPIView.as_view(), name='category-create'),
    path('categories/<int:id>/', views.CategoryDetailAPIView.as_view(), name='category-detail'),
    path('categories/<int:id>/update/', views.CategoryUpdateAPIView.as_view(), name='category-update'),
    path('categories/<int:id>/delete/', views.CategoryDeleteAPIView.as_view(), name='category-delete'),
    path('categories/<int:category_id>/products/', views.category_products, name='category-products'),
    path('categories/<int:category_id>/toggle-status/', views.toggle_category_status, name='toggle-category-status'),
    path('categories/stats/', views.category_stats, name='category-stats'),
]
