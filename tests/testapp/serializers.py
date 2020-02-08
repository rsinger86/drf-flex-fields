from rest_framework import serializers
from rest_flex_fields import FlexFieldsModelSerializer
from tests.testapp.models import Pet, Person, Company


class CompanySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Company
        fields = ["name", "public"]


class PersonSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Person
        fields = ["name", "hobbies"]
        expandable_fields = {"employer": (CompanySerializer,)}


class PetSerializer(FlexFieldsModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all())

    class Meta:
        model = Pet
        fields = ["owner", "name", "toys", "species"]
        expandable_fields = {"owner": PersonSerializer}
