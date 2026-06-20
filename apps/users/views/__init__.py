
from apps.users.views.auth_views import RegisterView, LoginView, LogoutView
from apps.users.views.user_views import UserListView, UserDetailView

__all__ = [
    'RegisterView', 'LoginView', 'LogoutView',
    'UserListView', 'UserDetailView',
]