from collections import defaultdict


class ParallelOrderRecommender:
    """Recommends orders that can be cooked in parallel based on shared
    menu items with a quantity difference <= 1."""

    @staticmethod
    def recommend(orders, top_n: int = 7) -> dict:
        orders = list(orders)
        if not orders:
            return {}

        item_to_orders = defaultdict(list)
        item_lookup = {}
        for order in orders:
            for oi in order.order_items.select_related('menu_item__category').all():
                item_to_orders[oi.menu_item_id].append((order.id, oi.quantity))
                item_lookup[oi.menu_item_id] = oi.menu_item

        candidates = {order.id: {} for order in orders}
        for menu_item_id, order_qtys in item_to_orders.items():
            if len(order_qtys) < 2:
                continue
            mi = item_lookup[menu_item_id]
            for i in range(len(order_qtys)):
                oid1, qty1 = order_qtys[i]
                for j in range(i + 1, len(order_qtys)):
                    oid2, qty2 = order_qtys[j]
                    if abs(qty1 - qty2) <= 1:
                        shared = {
                            'menu_item_name': mi.name,
                            'category': mi.category.name,
                            'quantity_in_this': qty1,
                            'quantity_in_other': qty2,
                        }
                        candidates[oid1].setdefault(oid2, []).append(shared)
                        candidates[oid2].setdefault(oid1, []).append(
                            {**shared, 'quantity_in_this': qty2, 'quantity_in_other': qty1}
                        )

        result = {}
        for oid, rec_dict in candidates.items():
            if not rec_dict:
                continue
            rec_list = [
                {
                    'other_order_id': other_id,
                    'shared_items': shared_items,
                    '_score': (len(shared_items), -sum(abs(s['quantity_in_this'] - s['quantity_in_other']) for s in shared_items)),
                }
                for other_id, shared_items in rec_dict.items()
            ]
            rec_list.sort(key=lambda x: x['_score'], reverse=True)
            result[oid] = [{'other_order_id': r['other_order_id'], 'shared_items': r['shared_items']} for r in rec_list[:top_n]]
        return result