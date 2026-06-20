from django.urls import path
from apps.users.views import auth_views, user_views, restaurant_profile_views

urlpatterns = [
    path('auth/register/', auth_views.RegisterView.as_view(), name='register'),
    path('auth/login/', auth_views.LoginView.as_view(), name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Users
    path('users/', user_views.UserListView.as_view(), name='user-list'),
    path('users/me/', user_views.UserDetailView.as_view(), name='user-detail'),

     # Restaurant profiles
    # Owner (no user_id) – for restaurant users
    path(
        'restaurant-profiles/',
        restaurant_profile_views.RestaurantProfileOwnerView.as_view(),
        name='restaurant-profile-owner',
    ),
    # Admin (with user_id) – for admins
    path(
        'restaurant-profiles/<uuid:user_id>/',
        restaurant_profile_views.RestaurantProfileAdminView.as_view(),
        name='restaurant-profile-admin',
    ),
]
