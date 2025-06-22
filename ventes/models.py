from django.db import models
from clients.models import Client  # ← importer le bon modèle

class Interaction(models.Model):
    TYPE_CHOICES = [
        ('vente', 'Vente'),
        ('appel', 'Appel'),
        ('email', 'Email'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='interactions')
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    commentaire = models.TextField(blank=True)

    def __str__(self):
        return f"{self.client} - {self.type} - {self.date}"
