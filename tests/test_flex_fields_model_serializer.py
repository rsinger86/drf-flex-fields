from unittest.mock import MagicMock
from unittest import TestCase
from rest_framework import serializers
from django.utils.datastructures import MultiValueDict

from rest_flex_fields import FlexFieldsModelSerializer


class MockRequest(object):
    def __init__(self, query_params=MultiValueDict(), method="GET"):
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
        serializer.fields = {"cat": 1, "dog": 2, "zebra": 3}
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

    def test_get_omit_input_from_explicit_settings(self):
        serializer = FlexFieldsModelSerializer(context={})

        serializer.context["request"] = MockRequest(
            method="GET", query_params={"omit": "cat,dog"}
        )

        result = serializer._get_omit_input(["fish"])
        self.assertEqual(result, ["fish"])

    def test_get_omit_input_from_query_param(self):
        serializer = FlexFieldsModelSerializer(context={})

        serializer.context["request"] = MockRequest(
            method="GET", query_params=MultiValueDict({"omit": ["cat,dog"]})
        )

        result = serializer._get_omit_input([])
        self.assertEqual(result, ["cat", "dog"])

    def test_get_fields_input_from_explicit_settings(self):
        serializer = FlexFieldsModelSerializer(context={})

        serializer.context["request"] = MockRequest(
            method="GET", query_params={"fields": "cat,dog"}
        )

        result = serializer._get_fields_input(["fish"])
        self.assertEqual(result, ["fish"])

    def test_get_fields_input_from_query_param(self):
        serializer = FlexFieldsModelSerializer(context={})

        serializer.context["request"] = MockRequest(
            method="GET", query_params=MultiValueDict({"fields": ["cat,dog"]})
        )

        result = serializer._get_fields_input([])
        self.assertEqual(result, ["cat", "dog"])

    def test_get_expand_input_from_explicit_setting(self):
        serializer = FlexFieldsModelSerializer(context={})

        serializer.context["request"] = MockRequest(
            method="GET", query_params={"fields": "cat,dog"}
        )

        result = serializer._get_expand_input(["cat"])
        self.assertEqual(result, ["cat"])

    def test_get_expand_input_from_query_param(self):
        serializer = FlexFieldsModelSerializer(context={})

        serializer.context["request"] = MockRequest(
            method="GET", query_params=MultiValueDict({"expand": ["cat,dog"]})
        )

        result = serializer._get_expand_input([])
        self.assertEqual(result, ["cat", "dog"])

    def test_get_expand_input_from_query_param_limit_to_list_permitted(self):
        serializer = FlexFieldsModelSerializer(context={})

        serializer.context["request"] = MockRequest(
            method="GET", query_params=MultiValueDict({"expand": ["cat,dog"]})
        )

        serializer.context["permitted_expands"] = ["cat"]
        result = serializer._get_expand_input([])
        self.assertEqual(result, ["cat"])

    def test_parse_request_list_value(self):
        test_params = [
            {"abc": ["cat,dog,mouse"]},
            {"abc": ["cat", "dog", "mouse"]},
            {"abc[]": ["cat", "dog", "mouse"]},
        ]
        for query_params in test_params:
            serializer = FlexFieldsModelSerializer(context={})
            serializer.context["request"] = MockRequest(
                method="GET", query_params=MultiValueDict(query_params)
            )

            result = serializer._parse_request_list_value("abc")
            self.assertEqual(result, ["cat", "dog", "mouse"])

    def test_parse_request_list_value_empty_if_cannot_access_request(self):
        serializer = FlexFieldsModelSerializer(context={})
        result = serializer._parse_request_list_value("abc")
        self.assertEqual(result, [])

    def test_import_serializer_class(self):
        pass

    def test_make_expanded_field_serializer(self):
        pass
