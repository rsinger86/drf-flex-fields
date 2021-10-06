from functools import lru_cache
from typing import Optional

from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import QuerySet
from rest_framework.compat import coreapi, coreschema
from rest_framework.filters import BaseFilterBackend
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet

from rest_flex_fields.serializers import FlexFieldsSerializerMixin


class FlexFieldsFilterBackend(BaseFilterBackend):
    def filter_queryset(
        self, request: Request, queryset: QuerySet, view: GenericViewSet
    ):
        if (
            not issubclass(view.get_serializer_class(), FlexFieldsSerializerMixin)
            or request.method != "GET"
        ):
            return queryset

        auto_remove_fields_from_query = getattr(
            view, "auto_remove_fields_from_query", True
        )
        auto_select_related_on_query = getattr(
            view, "auto_select_related_on_query", True
        )
        required_query_fields = list(getattr(view, "required_query_fields", []))

        serializer = view.get_serializer(  # type: FlexFieldsSerializerMixin
            context=view.get_serializer_context()
        )

        serializer.apply_flex_fields(serializer.fields, serializer._flex_options_rep_only)
        serializer._flex_fields_rep_applied = True

        model_fields = [
            self._get_field(field.source, queryset.model)
            for field in serializer.fields.values()
            if self._get_field(field.source, queryset.model)
        ]

        nested_model_fields = [
            self._get_field(field.source, queryset.model)
            for field in serializer.fields.values()
            if self._get_field(field.source, queryset.model)
            and field.field_name in serializer.expanded_fields
        ]

        if auto_remove_fields_from_query:
            queryset = queryset.only(
                *(
                    required_query_fields
                    + [
                        model_field.name
                        for model_field in model_fields
                        if not model_field.is_relation or model_field.many_to_one
                    ]
                )
            )

        if auto_select_related_on_query and nested_model_fields:
            queryset = queryset.select_related(
                *(
                    model_field.name
                    for model_field in nested_model_fields
                    if model_field.is_relation and model_field.many_to_one
                )
            )

            queryset = queryset.prefetch_related(
                *(
                    model_field.name
                    for model_field in nested_model_fields
                    if model_field.is_relation and not model_field.many_to_one
                )
            )

        return queryset

    @staticmethod
    @lru_cache()
    def _get_field(field_name: str, model: models.Model) -> Optional[models.Field]:
        try:
            # noinspection PyProtectedMember
            return model._meta.get_field(field_name)
        except FieldDoesNotExist:
            return None

    def get_schema_fields(self, view):
        assert (
            coreapi is not None
        ), "coreapi must be installed to use `get_schema_fields()`"
        assert (
            coreschema is not None
        ), "coreschema must be installed to use `get_schema_fields()`"

        if not issubclass(view.get_serializer_class(), FlexFieldsSerializerMixin):
            return []

        return [
            coreapi.Field(
                name="fields",
                required=False,
                location="query",
                schema=coreschema.String(
                    title="Selected fields",
                    description="Specify required field by comma",
                ),
                example="field1,field2,nested.field",
            ),
            coreapi.Field(
                name="omit",
                required=False,
                location="query",
                schema=coreschema.String(
                    title="Omitted fields",
                    description="Specify required field by comma",
                ),
                example="field1,field2,nested.field",
            ),
            coreapi.Field(
                name="expand",
                required=False,
                location="query",
                schema=coreschema.String(
                    title="Expanded fields",
                    description="Specify required nested items by comma",
                ),
                example="nested1,nested2",
            ),
        ]

    def get_schema_operation_parameters(self, view):

        if not issubclass(view.get_serializer_class(), FlexFieldsSerializerMixin):
            return []

        parameters = [
            {
                "name": "fields",
                "required": False,
                "in": "query",
                "description": "Specify required field by comma",
                "schema": {
                    "title": "Selected fields",
                    "type": "string",
                },
                "example": "field1,field2,nested.field",
            },
            {
                "name": "omit",
                "required": False,
                "in": "query",
                "description": "Specify required field by comma",
                "schema": {
                    "title": "Omitted fields",
                    "type": "string",
                },
                "example": "field1,field2,nested.field",
            },
            {
                "name": "expand",
                "required": False,
                "in": "query",
                "description": "Specify required field by comma",
                "schema": {
                    "title": "Expanded fields",
                    "type": "string",
                },
                "example": "nested1,nested2",
            },
        ]

        return parameters
