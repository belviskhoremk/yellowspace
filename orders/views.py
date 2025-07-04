from django.shortcuts import render
# Create your views here.

def cart(request):
    return render(request, 'cart.html')


from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Order, OrderItem
from .serializers import *
from products.serializers import ProductSerializer
from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .utils import PDFReceiptGenerator

@api_view(['GET'])
def download_receipt(request, order_id):
    """Download PDF receipt for an order"""
    try:
        order = Order.objects.get(id=order_id)

        # Generate PDF
        generator = PDFReceiptGenerator()
        pdf_buffer = generator.generate_receipt(order)

        # Create response
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_order_{order.id}.pdf"'

        return response

    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# Add this to your OrderCreateAPIView
class OrderCreateAPIView(generics.CreateAPIView):
    """
    Create a new order with items
    """
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            order = serializer.save()

            # Generate PDF receipt
            generator = PDFReceiptGenerator()
            pdf_buffer = generator.generate_receipt(order)

            # Return order with all details and PDF download link
            response_serializer = OrderDetailSerializer(order)
            response_data = response_serializer.data
            response_data['receipt_download_url'] = f'/api/orders/{order.id}/receipt/'

            return Response(response_data, status=status.HTTP_201_CREATED)


class OrderListAPIView(generics.ListAPIView):
    """
    List all orders
    """
    queryset = Order.objects.all().prefetch_related('items__product')
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by delivery status
        delivered = self.request.query_params.get('delivered')
        if delivered is not None:
            delivered_bool = delivered.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(delivered=delivered_bool)

        # Filter by customer name
        customer_name = self.request.query_params.get('customer_name')
        if customer_name:
            queryset = queryset.filter(customer_name__icontains=customer_name)

        # Filter by phone number
        phone = self.request.query_params.get('phone')
        if phone:
            queryset = queryset.filter(phone_number__icontains=phone)

        return queryset.order_by('-ordered_at')


class OrderDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve a specific order
    """
    queryset = Order.objects.all().prefetch_related('items__product')
    serializer_class = OrderDetailSerializer
    lookup_field = 'id'


class OrderUpdateAPIView(generics.UpdateAPIView):
    """
    Update order details (mainly for delivery status)
    """
    queryset = Order.objects.all()
    serializer_class = OrderUpdateSerializer
    lookup_field = 'id'


@api_view(['PATCH'])
def mark_order_delivered(request, order_id):
    """
    Mark an order as delivered
    """
    order = get_object_or_404(Order, id=order_id)
    order.delivered = True
    order.save()

    serializer = OrderDetailSerializer(order)
    return Response({
        'message': f'Order #{order.id} marked as delivered',
        'order': serializer.data
    })


@api_view(['PATCH'])
def mark_order_pending(request, order_id):
    """
    Mark an order as pending (not delivered)
    """
    order = get_object_or_404(Order, id=order_id)
    order.delivered = False
    order.save()

    serializer = OrderDetailSerializer(order)
    return Response({
        'message': f'Order #{order.id} marked as pending',
        'order': serializer.data
    })


@api_view(['GET'])
def order_stats(request):
    """
    Get order statistics
    """
    total_orders = Order.objects.count()
    delivered_orders = Order.objects.filter(delivered=True).count()
    pending_orders = Order.objects.filter(delivered=False).count()

    return Response({
        'total_orders': total_orders,
        'delivered_orders': delivered_orders,
        'pending_orders': pending_orders,
        'delivery_rate': round((delivered_orders / total_orders * 100), 2) if total_orders > 0 else 0
    })


@api_view(['PATCH'])
def upload_payment_receipt(request, order_id):
    """
    Upload or update payment receipt for an order
    """
    order = get_object_or_404(Order, id=order_id)

    if 'paiement_confirmation' not in request.FILES:
        return Response({
            'error': 'No payment receipt file provided'
        }, status=status.HTTP_400_BAD_REQUEST)

    order.paiement_confirmation = request.FILES['paiement_confirmation']
    order.save()

    serializer = OrderDetailSerializer(order)
    return Response({
        'message': f'Payment receipt uploaded for Order #{order.id}',
        'order': serializer.data
    })


@api_view(['DELETE'])
def remove_payment_receipt(request, order_id):
    """
    Remove payment receipt from an order
    """
    order = get_object_or_404(Order, id=order_id)

    if order.paiement_confirmation:
        order.paiement_confirmation.delete()
        order.paiement_confirmation = None
        order.save()

        serializer = OrderDetailSerializer(order)
        return Response({
            'message': f'Payment receipt removed from Order #{order.id}',
            'order': serializer.data
        })
    else:
        return Response({
            'message': f'No payment receipt found for Order #{order.id}'
        }, status=status.HTTP_404_NOT_FOUND)