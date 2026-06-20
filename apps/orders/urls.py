from django.urls import path
from apps.orders.views import (
    OrderListCreateView,
    OrderDetailView,
    OrderStatusView,
    OrderSortedView,
    OrderVIPView,
    OrderNormalView,
    OrderPendingView,
    OrderRecommendationsView,
    OrderDetectSimpleView,
)

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/status/', OrderStatusView.as_view(), name='order-status-update'),
    path('sorted/', OrderSortedView.as_view(), name='order-sorted'),
    path('vip/', OrderVIPView.as_view(), name='order-vip'),
    path('normal/', OrderNormalView.as_view(), name='order-normal'),
    path('pending/', OrderPendingView.as_view(), name='order-pending'),
    path('recommendations/', OrderRecommendationsView.as_view(), name='order-recommendations'),
    path('detect-simple/', OrderDetectSimpleView.as_view(), name='order-detect-simple'),
]
