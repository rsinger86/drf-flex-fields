from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from rest_flex_fields import FlexFieldsModelSerializer
from tests.testapp.models import Pet, PetStore, Person, Company, TaggedItem


class CompanySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Company
        fields = ["name", "public"]


class PersonSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Person
        fields = ["name", "hobbies"]
        expandable_fields = {"employer": "tests.testapp.serializers.CompanySerializer"}


class PetStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = PetStore
        fields = ["id", "name"]


class PetSerializer(FlexFieldsModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all())
    sold_from = serializers.PrimaryKeyRelatedField(
        queryset=PetStore.objects.all(), allow_null=True
    )
    diet = serializers.CharField()

    class Meta:
        model = Pet
        fields = ["owner", "name", "toys", "species", "diet", "sold_from"]

        expandable_fields = {
            "owner": "tests.testapp.PersonSerializer",
            "sold_from": "tests.testapp.PetStoreSerializer",
            "diet": serializers.SerializerMethodField,
        }

    def get_diet(self, obj):
        if obj.name == "Garfield":
            return "homemade lasanga"
        return "pet food"


class TaggedItemSerializer(FlexFieldsModelSerializer):
    content_object = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TaggedItem
        fields = (
            "id",
            "content_type",
            "object_id",
            "content_object"
        )
