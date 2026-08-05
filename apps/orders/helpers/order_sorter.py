class OrderSorter:
    """
    Ranks orders for the kitchen display.

    Rule: VIP orders (special_flag=True) always outrank normal orders.
    Among normal orders, higher priority_score = more urgent = ranked first.

    Order.id is a UUID (no numeric sequence), so:
      - VIP tie-breaking uses id directly (UUID supports ordering via __lt__).
      - Windowing uses chronological position (created_at), never id arithmetic.
    """

    @staticmethod
    def _sort_key(order):
        # (0, ...) always sorts before (1, ...) -> VIP first, in one pass,
        # no separate specials/normals lists needed.
        if order.special_flag:
            return (0, order.created_at)
        return (1, order.priority_score)

    @classmethod
    def sort_without_window(cls, orders):
        """Global sort: VIP first (by id), then normals by priority_score desc."""
        return sorted(orders, key=cls._sort_key)

    @classmethod
    def sort_with_window(cls, orders, window_size: int = 10):
        """
        Buckets orders into fixed-size chronological batches (oldest first),
        then applies the VIP-first / score ordering inside each batch.
        """
        if not orders:
            return []

        chronological = sorted(orders, key=lambda o: o.created_at)

        result, window = [], []
        for idx, order in enumerate(chronological):
            window.append(order)
            if (idx + 1) % window_size == 0:
                result.extend(sorted(window, key=cls._sort_key))
                window = []  
        if window:
            result.extend(sorted(window, key=cls._sort_key))
        return result

    @staticmethod
    def get_vip_orders(orders):
        return sorted([o for o in orders if o.special_flag], key=lambda o: o.created_at)

    @staticmethod
    def get_normal_orders(orders):
        return sorted([o for o in orders if not o.special_flag],
                      key=lambda o: o.priority_score, reverse=True)
        
    @classmethod
    def sort_normal_with_window(cls, orders, window_size: int = 10):
        """Windows only normal (non-VIP) orders, sorted by priority_score
        desc within each chronological window. VIP orders are excluded."""
        normals = [o for o in orders if not o.special_flag]
        return cls.sort_with_window(normals, window_size=window_size)