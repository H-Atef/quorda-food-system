from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from apps.users.serializers import RestaurantProfileSerializer
from apps.users.permissions import IsRestaurant, IsAdmin
from apps.users.services.restaurant_profile_service import RestaurantProfileService


# ------------------------------------------------------------------
# Base mixin to share CRUD logic (DRY)
# ------------------------------------------------------------------
class RestaurantProfileMixin:
    def _perform_update(self, profile, data, partial, request):
        serializer = RestaurantProfileSerializer(profile, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        updated = RestaurantProfileService.update_profile(
            profile,
            serializer.validated_data,
            partial=partial,
            requesting_user=request.user,
        )
        return RestaurantProfileSerializer(updated).data

    def _perform_delete(self, profile, request):
        RestaurantProfileService.delete_profile(profile, requesting_user=request.user)


# ------------------------------------------------------------------
# View for restaurant owners – no user_id, always uses request.user
# ------------------------------------------------------------------
class RestaurantProfileOwnerView(APIView, RestaurantProfileMixin):
    permission_classes = [IsRestaurant]   # only restaurant users

    @extend_schema(
        summary="Get your own restaurant profile",
        operation_id="v1_users_restaurant_profiles_owner_retrieve",
        tags=['restaurant-profiles'],
        responses={
            200: OpenApiResponse(response=RestaurantProfileSerializer, description="Restaurant profile data"),
            403: OpenApiResponse(description="Forbidden", response=None),
            404: OpenApiResponse(description="Restaurant profile not found", response=None),
        }
    )
    def get(self, request):
        profile = RestaurantProfileService.get_profile_by_user_id(
            user_id=request.user.id,
            requesting_user=request.user,
        )
        return Response(RestaurantProfileSerializer(profile).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Full update your own restaurant profile",
        operation_id="v1_users_restaurant_profiles_owner_update",
        tags=['restaurant-profiles'],
        request=RestaurantProfileSerializer,
        responses={
            200: OpenApiResponse(response=RestaurantProfileSerializer, description="Updated restaurant profile data"),
            400: OpenApiResponse(description="Validation error", response=None),
            403: OpenApiResponse(description="Forbidden", response=None),
            404: OpenApiResponse(description="Restaurant profile not found", response=None),
        }
    )
    def put(self, request):
        profile = RestaurantProfileService.get_profile_by_user_id(
            user_id=request.user.id,
            requesting_user=request.user,
        )
        data = self._perform_update(profile, request.data, partial=False, request=request)
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Partial update your own restaurant profile",
        operation_id="v1_users_restaurant_profiles_owner_partial_update",
        tags=['restaurant-profiles'],
        request=RestaurantProfileSerializer,
        responses={
            200: OpenApiResponse(response=RestaurantProfileSerializer, description="Updated restaurant profile data"),
            400: OpenApiResponse(description="Validation error", response=None),
            403: OpenApiResponse(description="Forbidden", response=None),
            404: OpenApiResponse(description="Restaurant profile not found", response=None),
        }
    )
    def patch(self, request):
        profile = RestaurantProfileService.get_profile_by_user_id(
            user_id=request.user.id,
            requesting_user=request.user,
        )
        data = self._perform_update(profile, request.data, partial=True, request=request)
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete your own restaurant profile",
        operation_id="v1_users_restaurant_profiles_owner_destroy",
        tags=['restaurant-profiles'],
        responses={
            204: OpenApiResponse(description="Restaurant profile deleted successfully", response=None),
            403: OpenApiResponse(description="Forbidden", response=None),
            404: OpenApiResponse(description="Restaurant profile not found", response=None),
        }
    )
    def delete(self, request):
        profile = RestaurantProfileService.get_profile_by_user_id(
            user_id=request.user.id,
            requesting_user=request.user,
        )
        self._perform_delete(profile, request)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ------------------------------------------------------------------
# View for admins – requires user_id (path) to manage any profile
# ------------------------------------------------------------------
class RestaurantProfileAdminView(APIView, RestaurantProfileMixin):
    permission_classes = [IsAdmin]

    @extend_schema(
        summary="Get restaurant profile by user ID (admin only)",
        operation_id="v1_users_restaurant_profiles_admin_retrieve",
        tags=['restaurant-profiles'],
        parameters=[
            OpenApiParameter(
                'user_id',
                location=OpenApiParameter.PATH,  # <-- explicit PATH location
                description="User ID of the restaurant owner (not the profile ID)",
                type=str,
                required=True,
            )
        ],
        responses={
            200: OpenApiResponse(response=RestaurantProfileSerializer, description="Restaurant profile data"),
            403: OpenApiResponse(description="Forbidden", response=None),
            404: OpenApiResponse(description="Restaurant profile not found", response=None),
        }
    )
    def get(self, request, user_id):
        profile = RestaurantProfileService.get_profile_by_user_id(
            user_id=user_id,
            requesting_user=request.user,
        )
        return Response(RestaurantProfileSerializer(profile).data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Full update restaurant profile (admin only)",
        operation_id="v1_users_restaurant_profiles_admin_update",
        tags=['restaurant-profiles'],
        parameters=[
            OpenApiParameter(
                'user_id',
                location=OpenApiParameter.PATH,
                description="User ID of the restaurant owner (not the profile ID)",
                type=str,
                required=True,
            )
        ],
        request=RestaurantProfileSerializer,
        responses={
            200: OpenApiResponse(response=RestaurantProfileSerializer, description="Updated restaurant profile data"),
            400: OpenApiResponse(description="Validation error", response=None),
            403: OpenApiResponse(description="Forbidden", response=None),
            404: OpenApiResponse(description="Restaurant profile not found", response=None),
        }
    )
    def put(self, request, user_id):
        profile = RestaurantProfileService.get_profile_by_user_id(
            user_id=user_id,
            requesting_user=request.user,
        )
        data = self._perform_update(profile, request.data, partial=False, request=request)
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Partial update restaurant profile (admin only)",
        operation_id="v1_users_restaurant_profiles_admin_partial_update",
        tags=['restaurant-profiles'],
        parameters=[
            OpenApiParameter(
                'user_id',
                location=OpenApiParameter.PATH,
                description="User ID of the restaurant owner (not the profile ID)",
                type=str,
                required=True,
            )
        ],
        request=RestaurantProfileSerializer,
        responses={
            200: OpenApiResponse(response=RestaurantProfileSerializer, description="Updated restaurant profile data"),
            400: OpenApiResponse(description="Validation error", response=None),
            403: OpenApiResponse(description="Forbidden", response=None),
            404: OpenApiResponse(description="Restaurant profile not found", response=None),
        }
    )
    def patch(self, request, user_id):
        profile = RestaurantProfileService.get_profile_by_user_id(
            user_id=user_id,
            requesting_user=request.user,
        )
        data = self._perform_update(profile, request.data, partial=True, request=request)
        return Response(data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Delete restaurant profile (admin only)",
        operation_id="v1_users_restaurant_profiles_admin_destroy",
        tags=['restaurant-profiles'],
        parameters=[
            OpenApiParameter(
                'user_id',
                location=OpenApiParameter.PATH,
                description="User ID of the restaurant owner (not the profile ID)",
                type=str,
                required=True,
            )
        ],
        responses={
            204: OpenApiResponse(description="Restaurant profile deleted successfully", response=None),
            403: OpenApiResponse(description="Forbidden", response=None),
            404: OpenApiResponse(description="Restaurant profile not found", response=None),
        }
    )
    def delete(self, request, user_id):
        profile = RestaurantProfileService.get_profile_by_user_id(
            user_id=user_id,
            requesting_user=request.user,
        )
        self._perform_delete(profile, request)
        return Response(status=status.HTTP_204_NO_CONTENT)