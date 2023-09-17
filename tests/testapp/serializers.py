from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from rest_flex_fields.serializers import FlexFieldsModelSerializer, FlexFieldsSerializerMixin
from rest_flex_fields.fields import FlexSerializerMethodField
from tests.testapp.models import Pet, PetStore, Person, Company, TaggedItem, Country
from tests.testapp.utils import get_event_list

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


class EventSerializer(FlexFieldsSerializerMixin, serializers.Serializer):
    name = serializers.CharField()
    city = serializers.CharField()
    tickets = serializers.CharField()

    class Meta:
        expandable_fields = {
            "city": serializers.SerializerMethodField
        }
    
    def get_city(self, value):
        return { "name": value }


class CountrySerializer(FlexFieldsModelSerializer):
    events = FlexSerializerMethodField()
    
    class Meta:
        model = Country
        fields = ['name', 'events']

    def get_events(self, obj, expand, omit, fields):
        events = get_event_list(country=obj)
        return EventSerializer(events, many=True, expand=expand, omit=omit, fields=fields).data


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
    
    def get_info(self, obj, expand, fields, omit):
        {
            "is_vegetarian": obj.diet
        }

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
