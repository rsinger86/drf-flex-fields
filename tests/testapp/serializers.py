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
        expandable_fields = {"employer": "tests.testapp.serializers.CompanySerializer"}


class PetSerializer(FlexFieldsModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all())
    diet = serializers.CharField()

    class Meta:
        model = Pet
        fields = ["owner", "name", "toys", "species", "diet"]

        expandable_fields = {
            "owner": "tests.testapp.PersonSerializer",
            "diet": serializers.SerializerMethodField,
        }

    def get_diet(self, obj):
        if obj.name == "Garfield":
            return "homemade lasanga"
        return "pet food"
