from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

#class User(AbstractUser):
   # email = models.EmailField(unique=True)
    #USERNAME_FIELD = 'email'
   # REQUIRED_FIELDS = ['username']

   # def __str__(self):
   #     return self.email

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True, null=True)  # ← optionnel pour migration
    telephone = models.CharField(max_length=20, blank=True, null=True)  # ← optionnel pour migration
    entreprise = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"


# Create your models here.
