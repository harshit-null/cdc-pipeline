from rest_framework import viewsets
from .models import(Product, Customer, Order, OrderItem, InventoryMovement)
from .serializers import(ProductSerializer, CustomerSerializer, OrderSerializer, OrderItemSerializer, InventoryMovementSerializer)

# Create your views here.
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related("order", "product").all().order_by('id')
    serializer_class = OrderItemSerializer

class InventoryMovementViewSet(viewsets.ModelViewSet):
    queryset = InventoryMovement.objects.select_related("product").all().order_by('id')
    serializer_class = InventoryMovementSerializer