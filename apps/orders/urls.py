from django.urls import path
from apps.orders import views

urlpatterns = [
    # ---- restaurant-owner routes ----
    path('', views.OrderListCreateAPIView.as_view(), name='order-list-create'),
    path('vip/', views.VIPOrdersAPIView.as_view(), name='order-vip'),
    path('normal/windowed/', views.NormalOrdersWindowedAPIView.as_view(), name='order-normal-windowed'),
    path('windowed/', views.WindowedOrdersAPIView.as_view(), name='order-windowed'),
    path('by-creation-time/', views.OrdersByCreationTimeAPIView.as_view(), name='order-by-creation-time'),

    # ---- customer routes (delivery orders) ----
    path('customers/', views.CustomerOrderListCreateAPIView.as_view(), name='customer-order-list-create'),
    path('customers/<uuid:pk>/', views.CustomerOrderDetailAPIView.as_view(), name='customer-order-detail'),
    path('customers/<uuid:pk>/cancel/', views.CustomerOrderCancelAPIView.as_view(), name='customer-order-cancel'),

    # ---- restaurant-owner order detail / items ----
    path('<uuid:pk>/', views.OrderDetailAPIView.as_view(), name='order-detail'),
    path('<uuid:order_pk>/items/', views.OrderItemListCreateAPIView.as_view(), name='order-item-list-create'),
    path('<uuid:order_pk>/items/<uuid:pk>/', views.OrderItemDetailAPIView.as_view(), name='order-item-detail'),
]