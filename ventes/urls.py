from django.urls import path
from .views import InteractionCreateView, InteractionListView, InteractionListAllView

urlpatterns = [
    path('interactions/add/', InteractionCreateView.as_view(), name='interaction-add'),
    path('interactions/<int:client_id>/', InteractionListView.as_view(), name='interaction-list'),
    path('interactions/', InteractionListAllView.as_view(), name='interaction-list-all'),
]