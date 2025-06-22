from django.shortcuts import render
from rest_framework import status, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
#from .views import PasswordResetView
from rest_framework.permissions import IsAuthenticated, AllowAny
#from users.permissions import IsSuperUser
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import Group, Permission
from .models import User
from users.utils import APPLICATIONS, send_password_reset_email
from django.contrib.auth import get_user_model
from .permissions import IsSuperUser, IsInGroupWithPermission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.apps import apps
#from core.utils import APPLICATIONS, send_password_reset_email
from .serializers import (
    CustomTokenObtainPairSerializer, 
    GroupSerializer, 
    UserRegistrationSerializer, 
    UserSerializer,
    PasswordResetSerializer,
    PasswordChangeSerializer
)



##################################################################################
#############################-User Registration View-#############################
##################################################################################



class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    # def perform_create(self, serializer):
    #     user = serializer.save()
    #     send_password_reset_email(user, 'emails/password_reset_email.html')
    


###############################################################################
##############################-User ForgotPwd View-############################
###############################################################################



User = get_user_model()

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            send_password_reset_email(user, 'emails/forgot_password_email.html')
            return Response(
                {"message": "An email has been sent. Check your inbox and follow the instructions."},
                status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            # ⚠️ Optionnel : pour ne pas révéler si un email existe ou pas (sécurité)
            return Response(
                {"message": "If this email exists, a reset link has been sent."},
                status=status.HTTP_200_OK
            )



###############################################################################
###############################-User ResetPwd View-############################
###############################################################################


class ResetPasswordView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode('utf-8')
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                return Response({
                    "message": "Token valide, veuillez fournir un nouveau mot de passe."
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Token invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({"error": "Lien invalide ou corrompu."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode('utf-8')
            user = User.objects.get(pk=uid)

            if not default_token_generator.check_token(user, token):
                return Response({"error": "Token invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = PasswordResetSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Met à jour le mot de passe
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()

            # Renvoie un token JWT après reset
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Mot de passe réinitialisé avec succès.",
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


###############################################################################
##############################-User Change Pwd View-###########################
###############################################################################



class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "Please provide your old and new password to change it."
        })

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user

            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.is_first_login = False  
            user.save()

            update_session_auth_hash(request, user)  
            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


###############################################################################
##############################-SuperUser Perm View-############################
###############################################################################



class SuperUserPermissionViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]  

    def list(self, request):
        permissions = Permission.objects.all()
        permissions_data = []
        for perm in permissions:
            permissions_data.append({
                'id': perm.id,
                'name': perm.name,
                'codename': perm.codename,
                'content_type': perm.content_type.model
            })
        return Response(permissions_data)



###############################################################################
################################-Permissions View-#############################
###############################################################################



class PermissionViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        apps_to_check = APPLICATIONS  
        permissions_data = []
        
        for app_label in apps_to_check:
            app_models = apps.get_app_config(app_label).get_models()
            
            for model in app_models:
                model_name = model._name_
                try:
                    content_type = ContentType.objects.get_for_model(model)
                    
                    permissions = Permission.objects.filter(content_type=content_type)
                    
                    for perm in permissions:
                        permissions_data.append({
                            'id': perm.id,
                            'name': perm.name,
                            'codename': perm.codename,
                            'content_type': perm.content_type.model,
                        })
                except LookupError:
                    continue

        response_data = {
            'message': 'Permissions loaded successfully!',
            'permissions_data': permissions_data
        }
        
        return Response(response_data, status=status.HTTP_200_OK)



###############################################################################
#############################-Group Permission View-###########################
###############################################################################


class GroupPermissionViewSet(viewsets.ViewSet):
    permission_classes = [IsSuperUser]

    def update_permissions(self, request, pk=None):
        try:
            group = Group.objects.get(id=pk)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)

        permissions_data = request.data.get('permissions', []) 

        apps_to_check = APPLICATIONS
        valid_permissions = []

        for permission_id in permissions_data:
            try:
                permission = Permission.objects.get(id=permission_id)
                content_type = permission.content_type

                app_label = content_type.app_label
                if app_label in apps_to_check:
                    valid_permissions.append(permission)
            except Permission.DoesNotExist:
                continue

        try:

            group.permissions.set(valid_permissions)
            group.save()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Permissions updated successfully!"}, status=status.HTTP_200_OK)

    
###############################################################################
###################################-Group View-################################
###############################################################################



class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsSuperUser]



###############################################################################
###################################-User View-#################################
###############################################################################



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


    @action(detail=True, methods=['post'])
    def assign_group(self, request, pk=None):
        user = self.get_object()
        group_name = request.data.get('group')
        username = user.first_name

        if not request.user.is_staff:
            return Response({"error": "Only administrators can assign users to a group."}, status=status.HTTP_403_FORBIDDEN)

        try:
            group = Group.objects.get(name=group_name)
            if user.groups.filter(name=group_name).exists():
                return Response({"message": "User {username} already belong to this group."}, status=status.HTTP_400_BAD_REQUEST)
            user.groups.add(group)
            return Response({"message": f"User {username} has been added in {group_name}."}, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({"error": "Group Not Found!"}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['post'])
    def remove_group(self, request, pk=None):
        user = self.get_object()
        group_name = request.data.get('group')
        username = user.first_name

        if not request.user.is_staff:
            return Response({"error": "Only administrators can remove users from a group."}, status=status.HTTP_403_FORBIDDEN)
        try:
            group = Group.objects.get(name=group_name)
            user.groups.remove(group)
            return Response({"message": f"User {username} has been removed from {group_name}."}, status=status.HTTP_200_OK)
        except Group.DoesNotExist:
            return Response({"error": "Group Not Found!"}, status=status.HTTP_400_BAD_REQUEST)



###############################################################################
################################-Custom Token View-############################
###############################################################################



class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            new_token = token.access_token
            return Response({"access": str(new_token)})
        except TokenError as e:
            return Response({"detail": str(e)}, status=401)
        
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



###############################################################################
################################-Logout Token View-############################
###############################################################################



class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



###############################################################################
##################################-Protected View-#############################
###############################################################################



class ProtectedView(APIView):
    permission_classes = [IsSuperUser]

    def get(self, request):
        user = request.user
        token_info = request.auth

        return Response({
            "message": "Welcome",
            "first_name": token_info['first_name'],
            "last_name": token_info['last_name'],    
            "role": token_info['role']
        })
