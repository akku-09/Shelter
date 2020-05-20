
from rest_framework import viewsets

from component import models
from .serializers import MetadataSerializer,Metadata_Serializer
from .models import Metadata
from requests import request
class MetadataViewSet(viewsets.ModelViewSet):
    queryset = Metadata.objects.filter(type = 'C')
    serializer_class = MetadataSerializer

class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Metadata.objects.all()
    serializer_class = Metadata_Serializer

    def get_queryset(self):
        queryset = models.Metadata.objects.all()
        shelter_metadata_id = self.request.query_params.getlist('metadata_id', None)
        queryset = queryset.filter(id__in = shelter_metadata_id)
        return queryset

