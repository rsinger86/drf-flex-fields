from rest_framework.viewsets import ModelViewSet

from rest_flex_fields import FlexFieldsModelViewSet
from tests.testapp.models import Pet, TaggedItem
from tests.testapp.serializers import PetSerializer, TaggedItemSerializer


class PetViewSet(FlexFieldsModelViewSet):
    """
    API endpoint for testing purposes.
    """

    serializer_class = PetSerializer
    queryset = Pet.objects.all()
    permit_list_expands = ["owner"]


class TaggedItemViewSet(ModelViewSet):
    serializer_class = TaggedItemSerializer
    queryset = TaggedItem.objects.all()
