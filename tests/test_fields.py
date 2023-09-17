from django.test import TestCase
from django.urls import reverse
from tests.testapp.models import Country


class TestFlexSerializerMethodField(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        Country.objects.create(name="Germany")
        Country.objects.create(name="Spain")
        return super().setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        Country.objects.all().delete()
        return super().tearDownClass()

    def setUp(self) -> None:
        self.url = reverse("country-events-list")
        return super().setUp()

    def test_base_request(self):
        r = self.client.get(self.url)

        self.assertListEqual(
            r.json(),
            [
                {
                    "name": "Germany",
                    "events": [
                        {
                            "name": "Wacken Open Air",
                            "city": "Wacken",
                            "tickets": "www.example.com/wacken"
                        },
                        {
                            "name": "Full Force",
                            "city": "Grafenhainichen",
                            "tickets": "www.example.com/full_force"
                        }
                    ]
                },
                {
                    "name": "Spain",
                    "events": [
                        {
                            "name": "Resurrection",
                            "city": "Viveiro",
                            "tickets": "www.example.com/resurrection"
                        }
                    ]
                }
            ]
        )

    def test_omit_arg(self):
        r = self.client.get(self.url+"?omit=name,events.tickets")
        self.assertListEqual(
            r.json(),
            [
                {
                    "events": [
                        {
                            "name": "Wacken Open Air",
                            "city": "Wacken",
                        },
                        {
                            "name": "Full Force",
                            "city": "Grafenhainichen",
                        }
                    ]
                },
                {
                    "events": [
                        {
                            "name": "Resurrection",
                            "city": "Viveiro",
                        }
                    ]
                }
            ]
        )

    def test_fields_arg(self):
        r = self.client.get(self.url+"?fields=name,events.name")
        self.assertListEqual(
            r.json(),
            [
                {
                    "name": "Germany",
                    "events": [
                        {
                            "name": "Wacken Open Air"
                        },
                        {
                            "name": "Full Force"
                        }
                    ]
                },
                {
                    "name": "Spain",
                    "events": [
                        {
                            "name": "Resurrection"
                        }
                    ]
                }
            ]
        )

    def test_expand_arg(self):
        r = self.client.get(self.url+"?expand=events.city")
        self.assertListEqual(
            r.json(),
                [
                {
                    "name": "Germany",
                    "events": [
                        {
                            "name": "Wacken Open Air",
                            "city": {
                                "name": "Wacken",
                            },
                            "tickets": "www.example.com/wacken"
                        },
                        {
                            "name": "Full Force",
                            "city": {
                                "name": "Grafenhainichen",
                            },
                            "tickets": "www.example.com/full_force"
                        }
                    ]
                },
                {
                    "name": "Spain",
                    "events": [
                        {
                            "name": "Resurrection",
                            "city":  {
                                "name": "Viveiro",
                            },
                            "tickets": "www.example.com/resurrection"
                        }
                    ]
                }
            ]
        )

