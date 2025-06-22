from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    UserRegistrationView,
    ResetPasswordView,
    ForgotPasswordView,
    ChangePasswordView,
    UserViewSet,
    GroupViewSet,
    PermissionViewSet,
    GroupPermissionViewSet,
   
)
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'permissions', PermissionViewSet, basename='permission')

urlpatterns = [
    path('', include(router.urls)),
    path('user/register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='reset-password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('group/<int:pk>/update_permissions/', GroupPermissionViewSet.as_view({'post': 'update_permissions'})),
]