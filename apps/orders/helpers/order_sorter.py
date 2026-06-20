"""
OrderSorter — Django ORM-aware version.

Mirrors the original OrderSorter class:
  - sort_with_window   → window-based: specials by ID first, normals by priority_score
  - sort_without_window → specials by ID, then normals by priority_score
  - get_vip_orders     → only special_flag=True, sorted by id
  - get_normal_orders  → only special_flag=False, sorted by priority_score desc
"""
from apps.orders.helpers.priority_calculator import PriorityCalculator


class OrderSorter:

    @staticmethod
    def sort_with_window(orders, window_size: int = 10):
        """Window-based sorting. Lower window first; within each window specials by ID then normals by score."""
        if not orders:
            return []

        windows = {}
        for order in orders:
            win_idx = (order.id - 1) // window_size
            windows.setdefault(win_idx, []).append(order)

        result = []
        for win_idx in sorted(windows.keys()):
            win_orders = windows[win_idx]
            specials = sorted([o for o in win_orders if o.special_flag], key=lambda o: o.id)
            normals = sorted(
                [o for o in win_orders if not o.special_flag],
                key=lambda o: PriorityCalculator.compute_score(o),
                reverse=True,
            )
            result.extend(specials)
            result.extend(normals)
        return result

    @staticmethod
    def sort_without_window(orders):
        """Global sort: specials by ID, then normals by priority score."""
        specials = sorted([o for o in orders if o.special_flag], key=lambda o: o.id)
        normals = sorted(
            [o for o in orders if not o.special_flag],
            key=lambda o: PriorityCalculator.compute_score(o),
            reverse=True,
        )
        return specials + normals

    @staticmethod
    def get_vip_orders(orders):
        """Return only VIP (special_flag=True) orders sorted by ID ascending."""
        return sorted([o for o in orders if o.special_flag], key=lambda o: o.id)

    @staticmethod
    def get_normal_orders(orders):
        """Return only non-VIP orders sorted by priority_score descending."""
        return sorted(
            [o for o in orders if not o.special_flag],
            key=lambda o: PriorityCalculator.compute_score(o),
            reverse=True,
        )
