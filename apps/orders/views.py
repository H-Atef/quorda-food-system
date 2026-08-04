from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.orders.models import Order, OrderItem
from apps.orders.serializers import (
    OrderSerializer, OrderWriteSerializer,
    OrderItemReadSerializer, OrderItemWriteSerializer,
)
from apps.orders.permissions import IsRestaurantOwner, IsOrderItemOwner
from apps.orders.helpers.order_sorter import OrderSorter
from apps.orders.helpers.parallel_order_recommender import ParallelOrderRecommender


def _own_orders_qs(request):
    return (
        Order.objects.filter(restaurant=request.user.restaurant_profile)
        .prefetch_related('order_items__menu_item__category')
    )


def _get_owned_order(request, order_pk):
    """Fetch an order and enforce that it belongs to the requesting restaurant."""
    order = Order.objects.get(pk=order_pk)
    if order.restaurant_id != request.user.restaurant_profile.id:
        raise Order.DoesNotExist  # surfaces as 404, doesn't leak existence
    return order


WINDOW_SIZE_PARAM = OpenApiParameter(
    name='window_size',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    required=False,
    default=10,
    description='Number of orders per chronological window.',
)


@extend_schema(tags=['Orders'])
class OrderListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    @extend_schema(
        summary='List my orders',
        description="Returns all orders belonging to the authenticated restaurant.",
        responses=OrderSerializer(many=True),
    )
    def get(self, request):
        orders = _own_orders_qs(request)
        return Response(OrderSerializer(orders, many=True).data)

    @extend_schema(
        summary='Create an order',
        request=OrderWriteSerializer,
        responses={201: OrderSerializer},
    )
    def post(self, request):
        serializer = OrderWriteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Orders'])
class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    def get_object(self, request, pk):
        order = Order.objects.prefetch_related('order_items__menu_item__category').get(pk=pk)
        self.check_object_permissions(request, order)
        return order

    @extend_schema(summary='Retrieve an order', responses=OrderSerializer)
    def get(self, request, pk):
        order = self.get_object(request, pk)
        return Response(OrderSerializer(order).data)

    @extend_schema(summary='Replace an order', request=OrderWriteSerializer, responses=OrderSerializer)
    def put(self, request, pk):
        order = self.get_object(request, pk)
        serializer = OrderWriteSerializer(order, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data)

    @extend_schema(summary='Partially update an order', request=OrderWriteSerializer, responses=OrderSerializer)
    def patch(self, request, pk):
        order = self.get_object(request, pk)
        serializer = OrderWriteSerializer(order, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data)

    @extend_schema(summary='Delete an order', responses={204: None})
    def delete(self, request, pk):
        order = self.get_object(request, pk)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['Orders'])
class VIPOrdersAPIView(APIView):
    """GET: VIP-only orders (special_flag=True), sorted by id."""
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    @extend_schema(
        summary='List VIP orders',
        description='Returns only orders with special_flag=True, sorted by id ascending.',
        responses=OrderSerializer(many=True),
    )
    def get(self, request):
        orders = _own_orders_qs(request)
        vip = OrderSorter.get_vip_orders(orders)
        return Response(OrderSerializer(vip, many=True).data)


@extend_schema(tags=['Orders'])
class OrderRecommendationsAPIView(APIView):
    """GET: parallel-cooking recommendations for this restaurant's orders."""
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    @extend_schema(
        summary='Get parallel-cooking recommendations',
        description=(
            'For each order, returns up to 7 other orders that share menu items '
            'with a quantity difference <= 1, ranked by shared-item count then '
            'total quantity difference.'
        ),
        responses={200: OpenApiTypes.OBJECT},
    )
    def get(self, request):
        orders = _own_orders_qs(request)
        recommendations = ParallelOrderRecommender.recommend(orders)
        return Response(recommendations)


@extend_schema(tags=['Orders'])
class WindowedOrdersAPIView(APIView):
    """GET: orders grouped into chronological windows, VIP-first + priority sorted within each."""
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    @extend_schema(
        summary='List orders windowed (all orders)',
        description='Chronological windows of size window_size; VIP orders rank first within each window, normals sorted by priority_score desc.',
        parameters=[WINDOW_SIZE_PARAM],
        responses=OrderSerializer(many=True),
    )
    def get(self, request):
        window_size = int(request.query_params.get('window_size', 10))
        orders = _own_orders_qs(request)
        sorted_orders = OrderSorter.sort_with_window(orders, window_size=window_size)
        return Response(OrderSerializer(sorted_orders, many=True).data)


@extend_schema(tags=['Orders'])
class OrdersByCreationTimeAPIView(APIView):
    """GET: orders ordered by creation time (uses Order.Meta default ordering)."""
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    @extend_schema(
        summary='List orders by creation time',
        description='Orders sorted newest-first (Order.Meta.ordering = -created_at).',
        responses=OrderSerializer(many=True),
    )
    def get(self, request):
        orders = _own_orders_qs(request)
        return Response(OrderSerializer(orders, many=True).data)


@extend_schema(tags=['Orders'])
class NormalOrdersWindowedAPIView(APIView):
    """GET: non-VIP orders only, grouped into chronological windows and sorted by priority_score desc."""
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    @extend_schema(
        summary='List normal (non-VIP) orders windowed',
        description='Same windowing as /orders/windowed/ but excludes VIP orders entirely.',
        parameters=[WINDOW_SIZE_PARAM],
        responses=OrderSerializer(many=True),
    )
    def get(self, request):
        window_size = int(request.query_params.get('window_size', 10))
        orders = _own_orders_qs(request)
        sorted_orders = OrderSorter.sort_normal_with_window(orders, window_size=window_size)
        return Response(OrderSerializer(sorted_orders, many=True).data)


@extend_schema(tags=['Order Items'])
class OrderItemListCreateAPIView(APIView):
    """Items of one order. Creating/deleting items triggers the OrderItem
    post_save/post_delete signal, which recalculates the parent order's
    priority_score automatically — no manual recalc needed here."""
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    @extend_schema(summary='List items of an order', responses=OrderItemReadSerializer(many=True))
    def get(self, request, order_pk):
        order = _get_owned_order(request, order_pk)
        items = order.order_items.select_related('menu_item__category').all()
        return Response(OrderItemReadSerializer(items, many=True).data)

    @extend_schema(
        summary='Add an item to an order',
        request=OrderItemWriteSerializer,
        responses={201: OrderItemReadSerializer},
    )
    def post(self, request, order_pk):
        order = _get_owned_order(request, order_pk)
        serializer = OrderItemWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(order=order)
        return Response(OrderItemReadSerializer(item).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Order Items'])
class OrderItemDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsRestaurantOwner, IsOrderItemOwner]

    def get_object(self, request, order_pk, pk):
        order = _get_owned_order(request, order_pk)  # 404s if not owned
        item = order.order_items.select_related('menu_item__category').get(pk=pk)
        self.check_object_permissions(request, item)
        return item

    @extend_schema(summary='Retrieve an order item', responses=OrderItemReadSerializer)
    def get(self, request, order_pk, pk):
        item = self.get_object(request, order_pk, pk)
        return Response(OrderItemReadSerializer(item).data)

    @extend_schema(summary='Replace an order item', request=OrderItemWriteSerializer, responses=OrderItemReadSerializer)
    def put(self, request, order_pk, pk):
        item = self.get_object(request, order_pk, pk)
        serializer = OrderItemWriteSerializer(item, data=request.data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        return Response(OrderItemReadSerializer(item).data)

    @extend_schema(summary='Partially update an order item', request=OrderItemWriteSerializer, responses=OrderItemReadSerializer)
    def patch(self, request, order_pk, pk):
        item = self.get_object(request, order_pk, pk)
        serializer = OrderItemWriteSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        return Response(OrderItemReadSerializer(item).data)

    @extend_schema(summary='Delete an order item', responses={204: None})
    def delete(self, request, order_pk, pk):
        item = self.get_object(request, order_pk, pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)