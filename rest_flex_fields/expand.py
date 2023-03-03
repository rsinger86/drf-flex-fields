import copy
import importlib
from inspect import isclass
from typing import Any, Optional, Tuple, Type, Union

from django.db import models
from rest_framework import serializers
from rest_framework.fields import empty


def import_serializer_class(
    path: str, class_name: str
) -> Tuple[Optional[Type[serializers.Serializer]], Optional[str]]:
    try:
        module = importlib.import_module(path)
    except ImportError:
        return (
            None,
            f"No module found at path: {path} when trying to import {class_name}",
        )

    try:
        return getattr(module, class_name), None
    except AttributeError:
        return None, f"No class {path} class found in module {class_name}"


class Expand(object):
    """
    Simple class to track how a field gets expanded.
    Can be used directly in `Meta.expandable_fields` to provide
    typed interface when setting up fields.
    """

    _serializer_ref: Union[Type[serializers.Serializer], str]
    many: bool
    source: Optional[str]
    prefetch_model: Optional[Type[models.Model]] = None
    auto_prefetch: bool
    extra: dict

    def __init__(
        self,
        serializer_ref: Union[Type[serializers.Serializer], str],
        *,
        many: bool = empty,
        source: Optional[str] = None,
        auto_prefetch=False,
        prefetch_model: Optional[Type[models.Model]] = None,
        extra: Optional[dict] = None,
    ) -> None:
        self._serializer_ref = serializer_ref
        self.many = many
        self.source = source
        self.auto_prefetch = auto_prefetch
        self.prefetch_model = prefetch_model
        self.extra = extra or {}

    def resolve_string_import(self) -> Type[serializers.Serializer]:
        assert isinstance(self._serializer_ref, str)

        path_parts = self._serializer_ref.split(".")
        class_name = path_parts.pop()
        path = ".".join(path_parts)

        serializer_class, error = import_serializer_class(path, class_name)

        if error and not path.endswith(".serializers"):
            serializer_class, error = import_serializer_class(
                path + ".serializers", class_name
            )

        if serializer_class:
            return serializer_class

        raise Exception(error)

    def get_serializer_class(self) -> Type[serializers.Serializer]:
        if isinstance(self._serializer_ref, str):
            return self.resolve_string_import()
        elif isclass(self._serializer_ref) or issubclass(
            self._serializer_ref, serializers.Field
        ):
            return self._serializer_ref
        else:
            raise Exception("Could not determine serializer class.")

    def get_base_settings(self) -> dict:
        settings = {}

        if self.many != empty:
            settings["many"] = self.many

        if self.source is not None:
            settings["source"] = self.source

        settings.update(copy.deepcopy(self.extra))
        return settings

    @classmethod
    def init_from_legacy_def(cls, field_def: Any) -> "Expand":
        if isinstance(field_def, tuple) and len(field_def) == 2:
            serializer_ref, settings = field_def
            return Expand(
                serializer_ref,
                source=settings.get("source"),
                many=settings.get("many", False),
            )
        elif isinstance(field_def, str):
            return Expand(field_def)
        elif isclass(field_def) and issubclass(field_def, serializers.Field):
            return Expand(field_def)
        else:
            raise Exception(
                f"Error: {field_def} could not be cast to an Expand instance."
            )
