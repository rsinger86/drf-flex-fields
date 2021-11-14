from unittest.mock import patch

from django.test import TestCase
from django.utils.datastructures import MultiValueDict
from rest_framework import serializers

from rest_flex_fields.serializers import FlexFieldsModelSerializer
from tests.testapp.models import Company, Person, Pet
from tests.testapp.serializers import PetSerializer


class MockRequest(object):
    def __init__(self, query_params={}, method="GET"):
        self.query_params = query_params
        self.method = method


class TestSerialize(TestCase):
    def test_basic_field_omit(self):
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred"),
        )

        expected_serializer_data = {
            "name": "Garfield",
            "toys": "paper ball, string",
            "diet": "",
            "sold_from": None,
        }

        serializer = PetSerializer(pet, omit=["species", "owner"])
        self.assertEqual(serializer.data, expected_serializer_data)

        serializer = PetSerializer(pet, omit=(field for field in ("species", "owner")))
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_nested_field_omit(self):
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred", employer=Company(name="McDonalds")),
        )

        expected_serializer_data = {
            "diet": "",
            "name": "Garfield",
            "toys": "paper ball, string",
            "species": "cat",
            "owner": {"hobbies": "", "employer": {"name": "McDonalds"}},
            "sold_from": None,
        }

        serializer = PetSerializer(
            pet, expand=["owner.employer"], omit=["owner.name", "owner.employer.public"]
        )

        self.assertEqual(serializer.data, expected_serializer_data)

        serializer = PetSerializer(
            pet,
            expand=(field for field in ("owner.employer",)),
            omit=(field for field in ("owner.name", "owner.employer.public")),
        )
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_basic_field_include(self):
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred"),
        )

        expected_serializer_data = {"name": "Garfield", "toys": "paper ball, string"}

        serializer = PetSerializer(pet, fields=["name", "toys"])
        self.assertEqual(serializer.data, expected_serializer_data)

        serializer = PetSerializer(pet, fields=(field for field in ("name", "toys")))
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_nested_field_include(self):
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred", employer=Company(name="McDonalds")),
        )

        expected_serializer_data = {"owner": {"employer": {"name": "McDonalds"}}}

        serializer = PetSerializer(
            pet, expand=["owner.employer"], fields=["owner.employer.name"]
        )
        self.assertEqual(serializer.data, expected_serializer_data)

        serializer = PetSerializer(
            pet,
            expand=(field for field in ("owner.employer",)),
            fields=(field for field in ("owner.employer.name",)),
        )
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_basic_expand(self):
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred", hobbies="sailing"),
        )

        expected_serializer_data = {
            "name": "Garfield",
            "toys": "paper ball, string",
            "species": "cat",
            "owner": {"name": "Fred", "hobbies": "sailing"},
            "sold_from": None,
            "diet": "",
        }

        request = MockRequest(query_params=MultiValueDict({"expand": ["owner"]}))
        serializer = PetSerializer(pet, context={"request": request})
        self.assertEqual(serializer.data, expected_serializer_data)
        self.assertEqual(serializer.fields["owner"].context.get("request"), request)

        serializer = PetSerializer(pet, expand=(field for field in ("owner",)))
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_nested_expand(self):
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(
                name="Fred", hobbies="sailing", employer=Company(name="McDonalds")
            ),
        )

        expected_serializer_data = {
            "diet": "",
            "name": "Garfield",
            "toys": "paper ball, string",
            "species": "cat",
            "owner": {
                "name": "Fred",
                "hobbies": "sailing",
                "employer": {"public": False, "name": "McDonalds"},
            },
            "sold_from": None,
        }

        request = MockRequest(
            query_params=MultiValueDict({"expand": ["owner.employer"]})
        )
        serializer = PetSerializer(pet, context={"request": request})
        self.assertEqual(serializer.data, expected_serializer_data)
        self.assertEqual(
            serializer.fields["owner"].fields["employer"].context.get("request"),
            request,
        )

        serializer = PetSerializer(pet, expand=(field for field in ("owner.employer",)))
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_expand_from_request(self):
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(
                name="Fred", hobbies="sailing", employer=Company(name="McDonalds")
            ),
        )

        request = MockRequest(
            query_params=MultiValueDict({"expand": ["owner.employer"]})
        )
        serializer = PetSerializer(pet, context={"request": request})

        self.assertEqual(
            serializer.data,
            {
                "diet": "",
                "name": "Garfield",
                "toys": "paper ball, string",
                "species": "cat",
                "sold_from": None,
                "owner": {
                    "name": "Fred",
                    "hobbies": "sailing",
                    "employer": {"public": False, "name": "McDonalds"},
                },
            },
        )

    @patch("rest_flex_fields.serializers.EXPAND_PARAM", "include")
    def test_expand_with_custom_param_name(self):
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred", hobbies="sailing"),
        )

        expected_serializer_data = {
            "diet": "",
            "name": "Garfield",
            "toys": "paper ball, string",
            "species": "cat",
            "owner": {"name": "Fred", "hobbies": "sailing"},
            "sold_from": None,
        }

        serializer = PetSerializer(pet, include=["owner"])
        self.assertEqual(serializer.data, expected_serializer_data)

    @patch("rest_flex_fields.serializers.OMIT_PARAM", "exclude")
    def test_omit_with_custom_param_name(self):
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred"),
        )

        expected_serializer_data = {
            "name": "Garfield",
            "toys": "paper ball, string",
            "diet": "",
            "sold_from": None,
        }

        serializer = PetSerializer(pet, exclude=["species", "owner"])
        self.assertEqual(serializer.data, expected_serializer_data)

    @patch("rest_flex_fields.serializers.FIELDS_PARAM", "only")
    def test_fields_include_with_custom_param_name(self):
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred"),
        )

        expected_serializer_data = {"name": "Garfield", "toys": "paper ball, string"}

        serializer = PetSerializer(pet, only=["name", "toys"])
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_all_special_value_in_serialize(self):
        pet = Pet(
            name="Garfield",
            toys="paper ball, string",
            species="cat",
            owner=Person(name="Fred", employer=Company(name="McDonalds")),
        )

        class PetSerializer(FlexFieldsModelSerializer):
            owner = serializers.PrimaryKeyRelatedField(
                queryset=Person.objects.all(), allow_null=True
            )

            class Meta:
                model = Pet
                fields = "__all__"

        serializer = PetSerializer(
            fields=("name", "toys"),
            data={
                "name": "Garfield",
                "toys": "paper ball",
                "species": "cat",
                "owner": None,
                "diet": "lasanga",
            },
        )

        serializer.is_valid(raise_exception=True)
