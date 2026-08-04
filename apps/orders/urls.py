from django.urls import path
from apps.orders import views

urlpatterns = [
    path('', views.OrderListCreateAPIView.as_view(), name='order-list-create'),
    path('<uuid:pk>/', views.OrderDetailAPIView.as_view(), name='order-detail'),
    path('vip/', views.VIPOrdersAPIView.as_view(), name='order-vip'),
    path('recommendations/', views.OrderRecommendationsAPIView.as_view(), name='order-recommendations'),
    path('normal/windowed/', views.NormalOrdersWindowedAPIView.as_view(), name='order-normal-windowed'),
    path('windowed/', views.WindowedOrdersAPIView.as_view(), name='order-windowed'),
    path('by-creation-time/', views.OrdersByCreationTimeAPIView.as_view(), name='order-by-creation-time'),
    path('<uuid:order_pk>/items/', views.OrderItemListCreateAPIView.as_view(), name='order-item-list-create'),
    path('<uuid:order_pk>/items/<uuid:pk>/', views.OrderItemDetailAPIView.as_view(), name='order-item-detail'),
    
]