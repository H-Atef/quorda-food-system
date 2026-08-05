from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.orders.serializers import (
    OrderSerializer, OrderWriteSerializer,
    OrderItemReadSerializer, OrderItemWriteSerializer,
    CustomerOrderCreateSerializer, CustomerOrderUpdateSerializer,
)
from apps.orders.permissions import IsRestaurantOwner, IsOrderItemOwner, IsOrderCustomer
from apps.orders.services import OrderService, CustomerOrderService


WINDOW_SIZE_PARAM = OpenApiParameter(
    name='window_size',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.QUERY,
    required=False,
    default=10,
    description='Number of orders per chronological window.',
)


# ============================================================================
# Restaurant-owner endpoints
# ============================================================================

@extend_schema(tags=['Orders'])
class OrderListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    @extend_schema(
        summary='List orders',
        description="Returns all orders belonging to the authenticated restaurant.",
        responses=OrderSerializer(many=True),
    )
    def get(self, request):
        orders = OrderService.get_restaurant_orders_qs(request.user.restaurant_profile)
        return Response(OrderSerializer(orders, many=True).data)

    @extend_schema(
        summary='Create an order',
        request=OrderWriteSerializer,
        responses={201: OrderSerializer},
    )
    def post(self, request):
        serializer = OrderWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderService.create_order(
            request.user.restaurant_profile, serializer.validated_data
        )
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Orders'])
class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    @extend_schema(summary='Retrieve an order', responses=OrderSerializer)
    def get(self, request, pk):
        order = OrderService.get_owned_order(request.user.restaurant_profile, pk)
        return Response(OrderSerializer(order).data)

    @extend_schema(summary='Replace an order', request=OrderWriteSerializer, responses=OrderSerializer)
    def put(self, request, pk):
        order = OrderService.get_owned_order(request.user.restaurant_profile, pk)
        serializer = OrderWriteSerializer(order, data=request.data)
        serializer.is_valid(raise_exception=True)
        order = OrderService.update_order(order, serializer.validated_data)
        return Response(OrderSerializer(order).data)

    @extend_schema(summary='Partially update an order', request=OrderWriteSerializer, responses=OrderSerializer)
    def patch(self, request, pk):
        order = OrderService.get_owned_order(request.user.restaurant_profile, pk)
        serializer = OrderWriteSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        order = OrderService.update_order(order, serializer.validated_data)
        return Response(OrderSerializer(order).data)

    @extend_schema(summary='Delete an order', responses={204: None})
    def delete(self, request, pk):
        order = OrderService.get_owned_order(request.user.restaurant_profile, pk)
        OrderService.delete_order(order)
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
        vip = OrderService.get_vip_orders(request.user.restaurant_profile)
        return Response(OrderSerializer(vip, many=True).data)




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
        window_size = _parse_window_size(request)
        sorted_orders = OrderService.get_windowed_orders(request.user.restaurant_profile, window_size)
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
        orders = OrderService.get_restaurant_orders_qs(request.user.restaurant_profile)
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
        window_size = _parse_window_size(request)
        sorted_orders = OrderService.get_normal_windowed_orders(request.user.restaurant_profile, window_size)
        return Response(OrderSerializer(sorted_orders, many=True).data)


@extend_schema(tags=['Order Items'])
class OrderItemListCreateAPIView(APIView):
    """Items of one order. Creating/deleting items triggers the OrderItem
    post_save/post_delete signal, which recalculates the parent order's
    priority_score automatically — no manual recalc needed here."""
    permission_classes = [IsAuthenticated, IsRestaurantOwner]

    @extend_schema(summary='List items of an order', responses=OrderItemReadSerializer(many=True))
    def get(self, request, order_pk):
        order = OrderService.get_owned_order(request.user.restaurant_profile, order_pk)
        items = order.order_items.select_related('menu_item__category').all()
        return Response(OrderItemReadSerializer(items, many=True).data)

    @extend_schema(
        summary='Add an item to an order',
        request=OrderItemWriteSerializer,
        responses={201: OrderItemReadSerializer},
    )
    def post(self, request, order_pk):
        order = OrderService.get_owned_order(request.user.restaurant_profile, order_pk)
        serializer = OrderItemWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = OrderService.add_item(order, serializer.validated_data)
        return Response(OrderItemReadSerializer(item).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Order Items'])
class OrderItemDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsRestaurantOwner, IsOrderItemOwner]

    @extend_schema(summary='Retrieve an order item', responses=OrderItemReadSerializer)
    def get(self, request, order_pk, pk):
        _, item = OrderService.get_owned_item(request.user.restaurant_profile, order_pk, pk)
        return Response(OrderItemReadSerializer(item).data)

    @extend_schema(summary='Replace an order item', request=OrderItemWriteSerializer, responses=OrderItemReadSerializer)
    def put(self, request, order_pk, pk):
        _, item = OrderService.get_owned_item(request.user.restaurant_profile, order_pk, pk)
        serializer = OrderItemWriteSerializer(item, data=request.data)
        serializer.is_valid(raise_exception=True)
        item = OrderService.update_item(item, serializer.validated_data)
        return Response(OrderItemReadSerializer(item).data)

    @extend_schema(summary='Partially update an order item', request=OrderItemWriteSerializer, responses=OrderItemReadSerializer)
    def patch(self, request, order_pk, pk):
        _, item = OrderService.get_owned_item(request.user.restaurant_profile, order_pk, pk)
        serializer = OrderItemWriteSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        item = OrderService.update_item(item, serializer.validated_data)
        return Response(OrderItemReadSerializer(item).data)

    @extend_schema(summary='Delete an order item', responses={204: None})
    def delete(self, request, order_pk, pk):
        _, item = OrderService.get_owned_item(request.user.restaurant_profile, order_pk, pk)
        OrderService.delete_item(item)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# Customer endpoints (delivery orders: is_indoor=False)
# ============================================================================

@extend_schema(tags=['Customer Orders'])
class CustomerOrderListCreateAPIView(APIView):
    """GET: my delivery orders. POST: place a new delivery order."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='List my delivery orders',
        description='Returns all delivery orders (is_indoor=False) placed by the authenticated user.',
        responses=OrderSerializer(many=True),
    )
    def get(self, request):
        orders = CustomerOrderService.get_customer_orders_qs(request.user)
        return Response(OrderSerializer(orders, many=True).data)

    @extend_schema(
        summary='Place a new delivery order',
        description='Creates a delivery order (is_indoor is forced to False, customer is the authenticated user).',
        request=CustomerOrderCreateSerializer,
        responses={201: OrderSerializer},
    )
    def post(self, request):
        serializer = CustomerOrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        restaurant = validated_data.pop('restaurant')
        order = CustomerOrderService.create_order(request.user, restaurant, validated_data)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['Customer Orders'])
class CustomerOrderDetailAPIView(APIView):
    """GET: view my order. PATCH: modify my order (only while pending)."""
    permission_classes = [IsAuthenticated, IsOrderCustomer]

    def get_object(self, request, pk):
        order = CustomerOrderService.get_owned_order(request.user, pk)
        self.check_object_permissions(request, order)
        return order

    @extend_schema(summary='Retrieve my order', responses=OrderSerializer)
    def get(self, request, pk):
        order = self.get_object(request, pk)
        return Response(OrderSerializer(order).data)

    @extend_schema(
        summary='Modify my order',
        description='Replaces the order_items on a pending order. Fails with 400 if the order is no longer pending.',
        request=CustomerOrderUpdateSerializer,
        responses=OrderSerializer,
    )
    def patch(self, request, pk):
        order = self.get_object(request, pk)
        serializer = CustomerOrderUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        order = CustomerOrderService.update_order(order, serializer.validated_data)
        return Response(OrderSerializer(order).data)


@extend_schema(tags=['Customer Orders'])
class CustomerOrderCancelAPIView(APIView):
    """POST: cancel my order (allowed unless it's already done/cancelled)."""
    permission_classes = [IsAuthenticated, IsOrderCustomer]

    @extend_schema(
        summary='Cancel my order',
        description='Sets status to cancelled. Fails with 400 if the order is already done or cancelled.',
        request=None,
        responses=OrderSerializer,
    )
    def post(self, request, pk):
        order = CustomerOrderService.get_owned_order(request.user, pk)
        self.check_object_permissions(request, order)
        order = CustomerOrderService.cancel_order(order)
        return Response(OrderSerializer(order).data)


def _parse_window_size(request):
    """Small request-parsing helper — stays in the view layer since it's
    about interpreting an HTTP query param, not business logic."""
    raw = request.query_params.get('window_size', 10)
    try:
        window_size = int(raw)
    except (TypeError, ValueError):
        from rest_framework.exceptions import ValidationError
        raise ValidationError({'window_size': 'Must be an integer.'})
    if window_size < 1:
        from rest_framework.exceptions import ValidationError
        raise ValidationError({'window_size': 'Must be at least 1.'})
    return window_size