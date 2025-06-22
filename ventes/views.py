from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Interaction
from .serializers import InteractionSerializer

class InteractionCreateView(generics.CreateAPIView):
    queryset = Interaction.objects.all()
    serializer_class = InteractionSerializer

class InteractionListView(generics.ListAPIView):
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        client_id = self.kwargs['client_id']
        return Interaction.objects.filter(client_id=client_id, client__user=self.request.user).order_by('-date')

class InteractionListAllView(generics.ListAPIView):
    serializer_class = InteractionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Interaction.objects.filter(client__user=self.request.user).order_by('-date')
