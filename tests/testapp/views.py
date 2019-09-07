from rest_flex_fields import FlexFieldsModelViewSet
from tests.testapp.models import Pet
from tests.testapp.serializers import PetSerializer


class PetViewSet(FlexFieldsModelViewSet):
    """
    API endpoint for testing purposes.
    """

    serializer_class = PetSerializer
    queryset = Pet.objects.all()
    permit_list_expands = ["owner"]
