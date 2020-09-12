from django.test import TestCase

from rest_flex_fields import is_included, is_expanded


class MockRequest(object):
    def __init__(self, query_params={}, method="GET"):
        self.query_params = query_params
        self.method = method


class TestUtils(TestCase):
    def test_should_be_included(self):
        request = MockRequest(query_params={})
        self.assertTrue(is_included(request, "name"))

    def test_should_not_be_included(self):
        request = MockRequest(query_params={"omit": "name,address"})
        self.assertFalse(is_included(request, "name"))

    def test_should_not_be_included_and_due_to_omit_and_has_dot_notation(self):
        request = MockRequest(query_params={"omit": "friend.name,address"})
        self.assertFalse(is_included(request, "name"))

    def test_should_not_be_included_and_due_to_fields_and_has_dot_notation(self):
        request = MockRequest(query_params={"fields": "hobby,address"})
        self.assertFalse(is_included(request, "name"))

    def test_should_be_expanded(self):
        request = MockRequest(query_params={"expand": "name,address"})
        self.assertTrue(is_expanded(request, "name"))

    def test_should_not_be_expanded(self):
        request = MockRequest(query_params={"expand": "name,address"})
        self.assertFalse(is_expanded(request, "hobby"))

    def test_should_be_expanded_and_has_dot_notation(self):
        request = MockRequest(query_params={"expand": "person.name,address"})
        self.assertTrue(is_expanded(request, "name"))
