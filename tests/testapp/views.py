from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin

from rest_flex_fields import FlexFieldsModelViewSet
from tests.testapp.models import Pet, TaggedItem, Country
from tests.testapp.serializers import PetSerializer, TaggedItemSerializer, CountrySerializer


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


class CountryEventsViewset(GenericViewSet, ListModelMixin):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()
