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

    def test_filtering_events_fields(self):
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

        r = self.client.get(self.url+"?omit=events.tickets")
        self.assertListEqual(
            r.json(),
            [
                {
                    "name": "Germany",
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
                    "name": "Spain",
                    "events": [
                        {
                            "name": "Resurrection",
                            "city": "Viveiro",
                        }
                    ]
                }
            ]
        )
