"""
SimpleOrderDetector — Django ORM-aware version.

An order is "simple" if:
  - total_quantity <= criteria.max_quantity
  - max category priority among its items >= criteria.min_category_priority
"""


class SimpleOrderDetector:

    @staticmethod
    def detect(orders, criteria):
        """
        orders   : iterable of apps.orders.models.Order (pre-fetched order_items + menu_item + category)
        criteria : apps.restaurants.models.Criteria instance
        Returns  : list of matching Order instances
        """
        simple = []
        for order in orders:
            items = list(order.order_items.select_related('menu_item__category').all())
            total_qty = sum(i.quantity for i in items)
            if total_qty > criteria.max_quantity:
                continue
            max_cat_prio = max(
                (i.menu_item.category.priority for i in items),
                default=0,
            )
            if max_cat_prio >= criteria.min_category_priority:
                simple.append(order)
        return simple
