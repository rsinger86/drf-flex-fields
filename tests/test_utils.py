from django.test import TestCase

from rest_flex_fields import is_included, is_expanded, WILDCARD_ALL, WILDCARD_ASTERISK


class MockRequest(object):
    def __init__(self, query_params=None, method="GET"):
        if query_params is None:
            query_params = {}
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

    def test_is_expanded(self):
        test_cases = [
            ("a", "a", True),
            ("a", "b", False),
            ("a,b,c", "a", True),
            ("a,b,c", "b", True),
            ("a,b,c", "c", True),
            ("a,b,c", "d", False),
            ("a.b.c", "a", True),
            ("a.b.c", "a.b", True),
            ("a.b.c", "a.b.c", True),
            ("a.b.c", "b", False),
            ("a.b.c", "c", False),
            ("a.b.c", "d", False),
            ("a.b.c,d", "a", True),
            ("a.b.c,d", "d", True),
            (WILDCARD_ASTERISK, "a", True),
            (WILDCARD_ASTERISK, "a.b", False),
            (WILDCARD_ALL, "a", True),
            (WILDCARD_ALL, "a.b", False),
        ]
        for expand_query_arg, field, should_be_expanded in test_cases:
            request = MockRequest(query_params={"expand": expand_query_arg})
            self.assertEqual(is_expanded(request, field), should_be_expanded)
