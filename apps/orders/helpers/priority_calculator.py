from apps.orders.models import Order


class PriorityCalculator:
    TIME_WEIGHT = 0.4
    QUANTITY_WEIGHT = 0.4
    CATEGORY_WEIGHT = 0.2

    @staticmethod
    def _get_params(restaurant_profile):
        params = getattr(restaurant_profile, 'calculation_params', None)
        if params:
            params = params.first()
        if params:
            return {
                'time_weight': params.time_weight,
                'quantity_weight': params.quantity_weight,
                'category_weight': params.category_weight,
            }
        return {
            'time_weight': PriorityCalculator.TIME_WEIGHT,
            'quantity_weight': PriorityCalculator.QUANTITY_WEIGHT,
            'category_weight': PriorityCalculator.CATEGORY_WEIGHT,
        }

    @classmethod
    def compute_score(cls, order) -> float:
        items = list(order.order_items.select_related('menu_item__category').all())

        total_time = sum(i.menu_item.prep_time * i.quantity for i in items)
        total_qty = sum(i.quantity for i in items)
        category_boost = cls._category_boost(items)

        time_score = 1.0 / (total_time + 1)
        quantity_score = 1.0 / (total_qty + 1)
        category_score = min(category_boost, 10.0)

        params = cls._get_params(order.restaurant)
        return (
            params['time_weight'] * time_score
            + params['quantity_weight'] * quantity_score
            + params['category_weight'] * category_score
        )

    @staticmethod
    def _category_boost(items) -> float:
        boost = 0.0
        for item in items:
            category = getattr(item.menu_item, 'category', None)
            if category is None:
                continue
            prio = category.priority
            if prio > 1:
                boost += (prio - 1) * item.quantity
        return boost
