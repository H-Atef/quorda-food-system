from rest_framework.exceptions import NotFound
from apps.orders.models import Order
from apps.orders.helpers.order_sorter import OrderSorter
from apps.orders.helpers.detector import SimpleOrderDetector
from apps.orders.helpers.recommendation_engine import RecommendationEngine


class OrderService:

    # ── Base querysets ───────────────────────────────────────────────

    @staticmethod
    def _base_qs(restaurant_profile):
        """All orders for a restaurant with items pre-fetched."""
        return (
            Order.objects
            .filter(restaurant=restaurant_profile)
            .prefetch_related('order_items__menu_item__category')
        )

    @staticmethod
    def list_orders(restaurant_profile):
        return OrderService._base_qs(restaurant_profile)

    @staticmethod
    def get_by_id(order_id, restaurant_profile):
        try:
            return (
                OrderService._base_qs(restaurant_profile)
                .get(pk=order_id)
            )
        except Order.DoesNotExist:
            raise NotFound(f'Order {order_id} not found.')

    # ── Sorted / filtered views ──────────────────────────────────────

    @staticmethod
    def get_sorted(restaurant_profile, use_window: bool = True, window_size: int = 10):
        orders = list(OrderService._base_qs(restaurant_profile))
        if use_window:
            return OrderSorter.sort_with_window(orders, window_size)
        return OrderSorter.sort_without_window(orders)

    @staticmethod
    def get_vip(restaurant_profile):
        orders = list(OrderService._base_qs(restaurant_profile))
        return OrderSorter.get_vip_orders(orders)

    @staticmethod
    def get_normal(restaurant_profile):
        orders = list(OrderService._base_qs(restaurant_profile))
        return OrderSorter.get_normal_orders(orders)

    @staticmethod
    def get_pending(restaurant_profile):
        return OrderService._base_qs(restaurant_profile).filter(status=Order.Status.PENDING)

    # ── Recommendations ──────────────────────────────────────────────

    @staticmethod
    def get_recommendations(restaurant_profile, top_n: int = 7):
        orders = list(OrderService._base_qs(restaurant_profile))
        return RecommendationEngine.recommend_parallel_orders(orders, top_n=top_n)

    # ── Simple order detection ───────────────────────────────────────

    @staticmethod
    def detect_simple(restaurant_profile, criteria):
        orders = list(OrderService._base_qs(restaurant_profile))
        return SimpleOrderDetector.detect(orders, criteria)

    # ── Status update ────────────────────────────────────────────────

    @staticmethod
    def update_status(order, new_status: str):
        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        return order

    # ── Delete ───────────────────────────────────────────────────────

    @staticmethod
    def delete(order):
        order.delete()
