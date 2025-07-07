from django.db import models
from clients.models import Client  # ← importer le bon modèle

class Interaction(models.Model):
    TYPE_CHOICES = [
        ('vente', 'Vente'),
        ('achat', 'Achat'),
        ('appel', 'Appel téléphonique'),
        ('email', 'Email'),
        ('rdv', 'Rendez-vous'),
        ('sms', 'SMS'),
        ('support', 'Support client'),
        ('devis', 'Devis envoyé'),
        ('facture', 'Facture envoyée'),
        ('relance', 'Relance'),
        ('visite', 'Visite sur site'),
        ('demande_info', 'Demande d\'information'),
        ('reclamation', 'Réclamation'),
        ('remerciement', 'Remerciement'),
        ('prospection', 'Prospection'),
        ('autre', 'Autre'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='interactions')
    date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    commentaire = models.TextField(blank=True)

    def __str__(self):
        return f"{self.client} - {self.type} - {self.date}"
