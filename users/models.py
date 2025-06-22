from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
# from .managers import UserManager
# from core.helpers import profile_upload_to


AUTH_PROVIDERS = {
    'facebook': 'facebook',
    'google': 'google',
    'email': 'email'
}

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    last_name = models.CharField(max_length=30, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    auth_provider = models.CharField(
        max_length=255, blank=False, null=False,
        default=AUTH_PROVIDERS.get('email')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    notification_enabled = models.BooleanField(default=True)
    # profile_picture = models.ImageField(upload_to=profile_upload_to, blank=True, null=True)
   # country = models.ForeignKey('locations.Country', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    #city = models.ForeignKey('locations.City', on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
   # postal_code = models.CharField(max_length=20, null=True, blank=True)

    objects = UserManager()  # Correct ici

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
