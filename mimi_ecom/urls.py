"""
URL configuration for mimi_ecom project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from orders import views as order_views
from products import views as product_views
from .views import index, translate_text, setup_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('products/', product_views.products, name='products'),
    path('product-detail/<int:product_id>/', product_views.product_detail, name='product_detail'),
    path('cart/', order_views.cart, name='cart'),

    path('api/orders/', include('orders.urls')),
    path('api/products/', include('products.urls')),

    path('i18n/', include('django.conf.urls.i18n')),  # 👈 this enables language switching

    path('translate/', translate_text, name='translate_text'),
    path('setup-admin/', setup_admin, name='setup_admin'),

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)