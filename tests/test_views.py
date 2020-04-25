from http import HTTPStatus
from pprint import pprint
from unittest.mock import patch

from django.db import connection
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from rest_flex_fields.filter_backends import FlexFieldsFilterBackend
from tests.testapp.models import Company, Person, Pet


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
                "name": "Garfield",
                "toys": "paper ball, string",
                "species": "cat",
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

    def test_list_expanded(self):
        url = reverse("pet-list")
        url = url + "?expand=owner"
        response = self.client.get(url, format="json")

        self.assertEqual(
            response.data[0],
            {
                "name": "Garfield",
                "toys": "paper ball, string",
                "species": "cat",
                "owner": {"name": "Fred", "hobbies": "sailing"},
            },
        )

    def test_create_and_return_expanded_field(self):
        url = reverse("pet-list")
        url = url + "?expand=owner"

        response = self.client.post(
            url,
            {
                "owner": self.person.id,
                "species": "snake",
                "toys": "playstation",
                "name": "Freddy",
            },
            format="json",
        )

        self.assertEqual(
            response.data,
            {
                "name": "Freddy",
                "toys": "playstation",
                "species": "snake",
                "owner": {"name": "Fred", "hobbies": "sailing"},
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
