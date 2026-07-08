from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    CustomerViewSet,
    OrderViewSet, 
    OrderItemViewSet,
    InventoryMovementViewSet,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='orderitem') 
router.register(r'inventory-movements', InventoryMovementViewSet, basename='inventorymovement') 

urlpatterns = [
    path('', include(router.urls)),
]