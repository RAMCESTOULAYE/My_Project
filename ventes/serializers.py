from rest_framework import serializers
from .models import Interaction

class InteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interaction
        fields = ['id', 'client', 'date', 'type', 'commentaire']
        read_only_fields = ['date']