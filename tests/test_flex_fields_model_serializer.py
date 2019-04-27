from unittest.mock import MagicMock
from unittest import TestCase
from rest_framework import serializers

from rest_flex_fields import FlexFieldsModelSerializer


class MockRequest(object):
    def __init__(self, query_params={}, method="GET"):
        self.query_params = query_params
        self.method = method


class TestFlexFieldModelSerializer(TestCase):
    def test_field_should_not_exist_if_omitted(self):
        serializer = FlexFieldsModelSerializer()
        result = serializer._should_field_exist("name", ["name"], [], {})
        self.assertFalse(result)

    def test_field_should_not_exist_if_not_in_sparse(self):
        serializer = FlexFieldsModelSerializer()
        result = serializer._should_field_exist("name", [], ["age"], {})
        self.assertFalse(result)

    def test_field_should_exist_if_ommitted_but_is_parent_of_omit(self):
        serializer = FlexFieldsModelSerializer()

        result = serializer._should_field_exist(
            "employer", ["employer"], [], {"employer": ["address"]}
        )

        self.assertTrue(result)

    def test_clean_fields(self):
        serializer = FlexFieldsModelSerializer()
        serializer._fields = {"cat": 1, "dog": 2, "zebra": 3}
        serializer._clean_fields(["cat"], [], {})
        self.assertEqual(serializer.fields, {"dog": 2, "zebra": 3})

    def test_get_expanded_names_if_all(self):
        serializer = FlexFieldsModelSerializer()
        serializer.expandable_fields = {"cat": "field", "dog": "field"}
        result = serializer._get_expanded_names("*", [], [], {})
        self.assertEqual(result, ["cat", "dog"])

    def test_get_expanded_names_but_not_omitted(self):
        serializer = FlexFieldsModelSerializer()
        serializer.expandable_fields = {"cat": "field", "dog": "field"}
        result = serializer._get_expanded_names(["cat", "dog"], ["cat"], [], {})
        self.assertEqual(result, ["dog"])

    def test_get_expanded_names_but_only_sparse(self):
        serializer = FlexFieldsModelSerializer()
        serializer.expandable_fields = {"cat": "field", "dog": "field"}
        result = serializer._get_expanded_names(["cat"], [], ["cat"], {})
        self.assertEqual(result, ["cat"])

    def test_get_expanded_names_even_omitted_when_defer_to_next_level(self):
        serializer = FlexFieldsModelSerializer()
        serializer.expandable_fields = {"cat": "field", "dog": "field"}
        result = serializer._get_expanded_names(["cat"], ["cat"], [], {"cat": ["age"]})
        self.assertEqual(result, ["cat"])

    def test_cannot_access_request_if_not_root_serializer(self):
        serializer = FlexFieldsModelSerializer()
        serializer.parent = "Another serializer here"
        self.assertFalse(serializer._can_access_request)

    def test_cannot_access_request_if_no_context(self):
        serializer = FlexFieldsModelSerializer()
        self.assertFalse(serializer._can_access_request)

    def test_cannot_access_request_if_context_missing_request(self):
        serializer = FlexFieldsModelSerializer(context={})
        self.assertFalse(serializer._can_access_request)

    def test_cannot_access_request_if_request_method_is_not_get(self):
        serializer = FlexFieldsModelSerializer(
            context={"request": MockRequest(method="PUT")}
        )
        self.assertFalse(serializer._can_access_request)

    def test_can_access_request_if_request_method_is_get(self):
        serializer = FlexFieldsModelSerializer(
            context={"request": MockRequest(method="GET")}
        )
        self.assertTrue(serializer._can_access_request)

    def test_get_omit_input(self):
        return

    def test_get_fields_input(self):
        return

    def test_import_serializer_class(self):
        return

    def test_make_expanded_field_serializer(self):
        return
