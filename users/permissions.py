from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
#from users.permissions import IsSuperUser
import logging

logger = logging.getLogger(__name__)


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return bool(request.user and request.user.is_superuser)


class AdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            logger.info(f"Permission denied: User {request.user} is not authenticated.")
            return False
        
        if request.user.is_staff or request.user.groups.filter(name='Administrateurs').exists():
            return True
        else:
            logger.info(f"Permission denied: User {request.user} is not admin or part of 'Administrateurs'.")
            return False


class IsInGroupWithPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True

        # Permissions dont l'utilisateur a besoin selon son groupe
        group_permissions = request.user.groups.values_list('permissions__codename', flat=True)

        # Si l'utilisateur n'a pas de permissions dans ses groupes, refuser l'accès
        if not group_permissions:
            return False

        # Initialiser les variables pour vérifier chaque type de permission
        has_read_permission = False
        has_add_permission = False
        has_update_permission = False
        has_delete_permission = False

        # Récupérer le ContentType du modèle de la vue actuelle
        model_class = view.get_queryset().model  # ou récupérez le modèle autrement
        content_type = ContentType.objects.get_for_model(model_class)

        # Récupérer toutes les permissions associées à ce modèle via ContentType
        model_permissions = Permission.objects.filter(content_type=content_type).values_list('codename', flat=True)

        # Vérifier si l'utilisateur a les bonnes permissions pour ce modèle
        for permission in model_permissions:
            if permission in group_permissions:  # Vérifie si l'utilisateur a cette permission dans son groupe
                # Vérifie que la permission correspond bien au modèle actuel
                # Par exemple : si on vérifie pour un modèle 'project', on veut uniquement les permissions change_project, view_project, etc.
                permission_codename_model = permission.split('_')[1]  # On récupère la partie après le préfixe : 'project', 'activity', etc.
                
                # Si la permission est associée au bon modèle
                if permission_codename_model == model_class._meta.model_name:
                    if permission.startswith('view_'):
                        has_read_permission = True
                    elif permission.startswith('add_'):
                        has_add_permission = True
                    elif permission.startswith('change_'):
                        has_update_permission = True
                    elif permission.startswith('delete_'):
                        has_delete_permission = True

        # Logique pour la vérification en fonction de la méthode HTTP
        if request.method in SAFE_METHODS:
            return has_read_permission
        if request.method == 'POST':
            return has_add_permission
        if request.method in ['PUT', 'PATCH']:
            return has_update_permission
        if request.method == 'DELETE':
            return has_delete_permission

        return False