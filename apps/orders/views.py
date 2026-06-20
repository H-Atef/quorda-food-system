from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.restaurants.permissions import IsRestaurantOwner
from apps.orders.serializers import OrderSerializer, OrderStatusUpdateSerializer
from apps.orders.services import OrderService


def _get_restaurant_profile(request):
    return request.user.restaurant_profile


# ── Orders ───────────────────────────────────────────────────────────────────

class OrderListCreateView(APIView):
    
    permission_classes = [IsRestaurantOwner]

    @extend_schema(
        tags=['orders'],
        operation_id='v1_orders_list',
        summary='List all orders for the authenticated restaurant',
        responses={200: OpenApiResponse(response=OrderSerializer(many=True))},
    )
    def get(self, request):
        orders = OrderService.list_orders(_get_restaurant_profile(request))
        return Response(OrderSerializer(orders, many=True).data)

    @extend_schema(
        tags=['orders'],
        operation_id='v1_orders_create',
        summary='Create a new order',
        description='If is_indoor=false (delivery) customer FK is required. If is_indoor=true (dine-in) customer is optional.',
        request=OrderSerializer,
        responses={
            201: OpenApiResponse(response=OrderSerializer),
            400: OpenApiResponse(description='Validation error'),
        },
    )
    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(restaurant=_get_restaurant_profile(request))
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(APIView):
    
    permission_classes = [IsRestaurantOwner]

    def _get(self, request, pk):
        return OrderService.get_by_id(pk, _get_restaurant_profile(request))

    @extend_schema(
        tags=['orders'],
        operation_id='v1_orders_detail',
        summary='Retrieve an order',
        responses={200: OpenApiResponse(response=OrderSerializer), 404: OpenApiResponse(description='Not found')},
    )
    def get(self, request, pk):
        return Response(OrderSerializer(self._get(request, pk)).data)

    @extend_schema(
        tags=['orders'],
        operation_id='v1_orders_update',
        summary='Full update an order',
        request=OrderSerializer,
        responses={200: OpenApiResponse(response=OrderSerializer)},
    )
    def put(self, request, pk):
        order = self._get(request, pk)
        serializer = OrderSerializer(order, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(OrderSerializer(updated).data)

    @extend_schema(
        tags=['orders'],
        operation_id='v1_orders_partial_update',
        summary='Partial update an order',
        request=OrderSerializer,
        responses={200: OpenApiResponse(response=OrderSerializer)},
    )
    def patch(self, request, pk):
        order = self._get(request, pk)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(OrderSerializer(updated).data)

    @extend_schema(
        tags=['orders'],
        operation_id='v1_orders_delete',
        summary='Delete an order',
        responses={204: OpenApiResponse(description='Deleted')},
    )
    def delete(self, request, pk):
        OrderService.delete(self._get(request, pk))
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderStatusView(APIView):
    
    permission_classes = [IsRestaurantOwner]

    @extend_schema(
        tags=['orders'],
        operation_id='v1_orders_update_status',
        summary='Update order status',
        request=OrderStatusUpdateSerializer,
        responses={200: OpenApiResponse(response=OrderSerializer)},
    )
    def patch(self, request, pk):
        order = OrderService.get_by_id(pk, _get_restaurant_profile(request))
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = OrderService.update_status(order, serializer.validated_data['status'])
        return Response(OrderSerializer(updated).data)


class OrderSortedView(APIView):
    
    permission_classes = [IsRestaurantOwner]

    @extend_schema(
        tags=['orders'],
        operation_id='v1_orders_sorted',
        summary='Get all orders sorted (window or global)',
        parameters=[
            OpenApiParameter('use_window', bool, required=False, default=True,
                             description='Use window-based sorting (default true)'),
            OpenApiParameter('window_size', int, required=False, default=10,
                             description='Window size (default 10)'),
        ],
        responses={200: OpenApiResponse(response=OrderSerializer(many=True))},
    )
    def get(self, request):
        use_window = request.query_params.get('use_window', 'true').lower() != 'false'
        window_size = int(request.query_params.get('window_size', 10))
        orders = OrderService.get_sorted(_get_restaurant_profile(request), use_window, window_size)
        return Response(OrderSerializer(orders, many=True).data)


class OrderVIPView(APIView):
    
    permission_classes = [IsRestaurantOwner]

    @extend_schema(
        tags=['orders'],
        operation_id='v1_orders_vip',
        summary='Get VIP (special_flag=True) orders sorted by ID',
        responses={200: OpenApiResponse(response=OrderSerializer(many=True))},
    )
    def get(self, request):
        orders = OrderService.get_vip(_get_restaurant_profile(request))
        return Response(OrderSerializer(orders, many=True).data)


class OrderNormalView(APIView):
    
    permission_classes = [IsRestaurantOwner]

    @extend_schema(
        tags=['orders'],
        operation_id='v1_orders_normal',
        summary='Get normal (special_flag=False) orders sorted by priority score',
        responses={200: OpenApiResponse(response=OrderSerializer(many=True))},
    )
    def get(self, request):
        orders = OrderService.get_normal(_get_restaurant_profile(request))
        return Response(OrderSerializer(orders, many=True).data)


class OrderPendingView(APIView):
    
    permission_classes = [IsRestaurantOwner]

    @extend_schema(
        tags=['orders'],
        operation_id='v1_orders_pending',
        summary='Get all pending orders',
        responses={200: OpenApiResponse(response=OrderSerializer(many=True))},
    )
    def get(self, request):
        orders = OrderService.get_pending(_get_restaurant_profile(request))
        return Response(OrderSerializer(orders, many=True).data)


class OrderRecommendationsView(APIView):
    
    permission_classes = [IsRestaurantOwner]

    @extend_schema(
        tags=['orders'],
        operation_id='v1_orders_recommendations',
        summary='Get parallel cooking recommendations',
        description=(
            'For each order, lists other orders sharing at least one menu item '
            'with quantity difference ≤ 1. Returns top 7 per order by default.'
        ),
        parameters=[
            OpenApiParameter('top_n', int, required=False, default=7,
                             description='Max recommendations per order'),
        ],
        responses={200: OpenApiResponse(description='Dict of order_id → list of recommendations')},
    )
    def get(self, request):
        top_n = int(request.query_params.get('top_n', 7))
        data = OrderService.get_recommendations(_get_restaurant_profile(request), top_n=top_n)
        return Response(data)


class OrderDetectSimpleView(APIView):
    
    permission_classes = [IsRestaurantOwner]

    @extend_schema(
        tags=['orders'],
        summary='Detect simple orders using the restaurant\'s configured criteria',
        description=(
            'Uses the Criteria configured for this restaurant. '
            'Returns 404 if no criteria has been set yet.'
        ),
        responses={
            200: OpenApiResponse(response=OrderSerializer(many=True)),
            404: OpenApiResponse(description='No criteria configured for this restaurant'),
        },
    )
    def get(self, request):
        profile = _get_restaurant_profile(request)
        criteria = getattr(profile, 'criteria', None)
        if criteria is None:
            return Response(
                {'detail': 'No criteria configured for this restaurant. '
                           'Please POST to /api/v1/restaurants/criteria/ first.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        simple_orders = OrderService.detect_simple(profile, criteria)
        return Response(OrderSerializer(simple_orders, many=True).data)
