from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Order CRUD operations
    path('', views.OrderListAPIView.as_view(), name='order-list'),
    path('create/', views.OrderCreateAPIView.as_view(), name='order-create'),
    path('<int:id>/', views.OrderDetailAPIView.as_view(), name='order-detail'),
    path('<int:id>/update/', views.OrderUpdateAPIView.as_view(), name='order-update'),

    # Order status management
    path('<int:order_id>/deliver/', views.mark_order_delivered, name='mark-delivered'),
    path('<int:order_id>/pending/', views.mark_order_pending, name='mark-pending'),

    # Statistics
    path('stats/', views.order_stats, name='order-stats'),
    path('<int:order_id>/upload-receipt/', views.upload_payment_receipt, name='upload_payment_receipt'),
    path('<int:order_id>/remove-receipt/', views.remove_payment_receipt, name='remove_payment_receipt'),
    path('<int:order_id>/receipt/', views.download_receipt, name='download_receipt'),
]