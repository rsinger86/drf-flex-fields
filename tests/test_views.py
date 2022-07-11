from http import HTTPStatus
from pprint import pprint
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from rest_flex_fields.filter_backends import FlexFieldsFilterBackend
from tests.testapp.models import Company, Person, Pet, PetStore, TaggedItem


class PetViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name="McDonalds")

        self.person = Person.objects.create(
            name="Fred", hobbies="sailing", employer=self.company
        )

        self.pet = Pet.objects.create(
            name="Garfield", toys="paper ball, string", species="cat", owner=self.person
        )

    def tearDown(self):
        Company.objects.all().delete()
        Person.objects.all().delete()
        Pet.objects.all().delete()

    def test_retrieve_expanded(self):
        url = reverse("pet-detail", args=[self.pet.id])
        response = self.client.get(url + "?expand=owner", format="json")

        self.assertEqual(
            response.data,
            {
                "diet": "",
                "name": "Garfield",
                "toys": "paper ball, string",
                "species": "cat",
                "sold_from": None,
                "owner": {"name": "Fred", "hobbies": "sailing"},
            },
        )

    def test_retrieve_sparse(self):
        url = reverse("pet-detail", args=[self.pet.id])
        response = self.client.get(url + "?fields=name,species", format="json")

        self.assertEqual(response.data, {"name": "Garfield", "species": "cat"})

    def test_retrieve_sparse_and_deep_expanded(self):
        url = reverse("pet-detail", args=[self.pet.id])
        url = url + "?fields=owner&expand=owner.employer"
        response = self.client.get(url, format="json")

        self.assertEqual(
            response.data,
            {
                "owner": {
                    "name": "Fred",
                    "hobbies": "sailing",
                    "employer": {"public": False, "name": "McDonalds"},
                }
            },
        )

    def test_retrieve_all_fields_at_root_and_sparse_fields_at_next_level(self):
        url = reverse("pet-detail", args=[self.pet.id])
        url = url + "?fields=*,owner.name&expand=owner"
        response = self.client.get(url, format="json")

        self.assertEqual(
            response.data,
            {
                "name": "Garfield",
                "toys": "paper ball, string",
                "species": "cat",
                "diet": "",
                "sold_from": None,
                "owner": {
                    "name": "Fred",
                },
            },
        )

    def test_list_expanded(self):
        url = reverse("pet-list")
        url = url + "?expand=owner"
        response = self.client.get(url, format="json")

        self.assertEqual(
            response.data[0],
            {
                "diet": "",
                "name": "Garfield",
                "toys": "paper ball, string",
                "species": "cat",
                "sold_from": None,
                "owner": {"name": "Fred", "hobbies": "sailing"},
            },
        )

    def test_create_and_return_expanded_field(self):
        url = reverse("pet-list")
        url = url + "?expand=owner"

        response = self.client.post(
            url,
            {
                "diet": "rats",
                "owner": self.person.id,
                "species": "snake",
                "toys": "playstation",
                "name": "Freddy",
                "sold_from": None,
            },
            format="json",
        )

        self.assertEqual(
            response.data,
            {
                "name": "Freddy",
                "diet": "rats",
                "toys": "playstation",
                "sold_from": None,
                "species": "snake",
                "owner": {"name": "Fred", "hobbies": "sailing"},
            },
        )

    def test_expand_drf_serializer_field(self):
        url = reverse("pet-detail", args=[self.pet.id])
        response = self.client.get(url + "?expand=diet", format="json")

        self.assertEqual(
            response.data,
            {
                "diet": "homemade lasanga",
                "name": "Garfield",
                "toys": "paper ball, string",
                "sold_from": None,
                "species": "cat",
                "owner": self.pet.owner_id,
            },
        )

    def test_expand_drf_model_serializer(self):
        petco = PetStore.objects.create(name="PetCo")
        self.pet.sold_from = petco
        self.pet.save()

        url = reverse("pet-detail", args=[self.pet.id])
        response = self.client.get(url + "?expand=sold_from", format="json")

        self.assertEqual(
            response.data,
            {
                "diet": "",
                "name": "Garfield",
                "toys": "paper ball, string",
                "sold_from": {"id": petco.id, "name": "PetCo"},
                "species": "cat",
                "owner": self.pet.owner_id,
            },
        )


@override_settings(DEBUG=True)
@patch("tests.testapp.views.PetViewSet.filter_backends", [FlexFieldsFilterBackend])
class PetViewWithSelectFieldsFilterBackendTests(PetViewTests):
    def test_query_optimization(self):
        url = reverse("pet-list")
        url = url + "?expand=owner&fields=name,owner"

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.assertEqual(len(connection.queries), 1)
        self.assertEqual(
            connection.queries[0]["sql"],
            (
                "SELECT "
                '"testapp_pet"."id", '
                '"testapp_pet"."name", '
                '"testapp_pet"."owner_id", '
                '"testapp_person"."id", '
                '"testapp_person"."name", '
                '"testapp_person"."hobbies", '
                '"testapp_person"."employer_id" '
                'FROM "testapp_pet" '
                'INNER JOIN "testapp_person" ON ("testapp_pet"."owner_id" = "testapp_person"."id")'
            ),
        )

    # todo: test many to one
    # todo: test many to many
    # todo: test view options for SelectFieldsFilterBackend


@override_settings(DEBUG=True)
@patch("tests.testapp.views.TaggedItemViewSet.filter_backends", [FlexFieldsFilterBackend])
class TaggedItemViewWithSelectFieldsFilterBackendTests(APITestCase):
    def test_query_optimization_includes_generic_foreign_keys_in_prefetch_related(self):
        self.company = Company.objects.create(name="McDonalds")

        self.person = Person.objects.create(
            name="Fred", hobbies="sailing", employer=self.company
        )

        self.pet1 = Pet.objects.create(
            name="Garfield", toys="paper ball, string", species="cat",
            owner=self.person
        )
        self.pet2 = Pet.objects.create(
            name="Garfield", toys="paper ball, string", species="cat",
            owner=self.person
        )

        self.tagged_item1 = TaggedItem.objects.create(
            content_type=ContentType.objects.get_for_model(Pet),
            object_id=self.pet1.id
        )
        self.tagged_item2 = TaggedItem.objects.create(
            content_type=ContentType.objects.get_for_model(Pet),
            object_id=self.pet2.id
        )
        self.tagged_item3 = TaggedItem.objects.create(
            content_type=ContentType.objects.get_for_model(Person),
            object_id=self.person.id
        )
        self.tagged_item4 = TaggedItem.objects.create(
            content_type=ContentType.objects.get_for_model(Company),
            object_id=self.company.id
        )

        url = reverse("tagged-item-list")

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(connection.queries), 4)

        self.assertEqual(
            connection.queries[0]["sql"],
            (
                'SELECT '
                '"testapp_taggeditem"."id", '
                '"testapp_taggeditem"."content_type_id", '
                '"testapp_taggeditem"."object_id", '
                '"django_content_type"."id", '
                '"django_content_type"."app_label", '
                '"django_content_type"."model" '
                'FROM "testapp_taggeditem" '
                'INNER JOIN "django_content_type" ON ("testapp_taggeditem"."content_type_id" = "django_content_type"."id")'
            ))
        self.assertEqual(
            connection.queries[1]["sql"],
            (
                'SELECT '
                '"testapp_pet"."id", '
                '"testapp_pet"."name", '
                '"testapp_pet"."toys", '
                '"testapp_pet"."species", '
                '"testapp_pet"."owner_id", '
                '"testapp_pet"."sold_from_id", '
                '"testapp_pet"."diet" '
                'FROM "testapp_pet" WHERE "testapp_pet"."id" IN ({0}, {1})'.format(self.pet1.id, self.pet2.id)
            )
        )
        self.assertEqual(
            connection.queries[2]["sql"],
            (
                'SELECT '
                '"testapp_person"."id", '
                '"testapp_person"."name", '
                '"testapp_person"."hobbies", '
                '"testapp_person"."employer_id" '
                'FROM "testapp_person" WHERE "testapp_person"."id" IN ({0})'.format(self.person.id)
            )
        )
        self.assertEqual(
            connection.queries[3]["sql"],
            (
                'SELECT '
                '"testapp_company"."id", '
                '"testapp_company"."name", '
                '"testapp_company"."public" '
                'FROM "testapp_company" WHERE "testapp_company"."id" IN ({0})'.format(self.company.id)
            )
        )

        self.assertEqual(len(response.json()), 4)