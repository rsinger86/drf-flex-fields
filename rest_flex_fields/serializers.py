import copy
import importlib

from rest_framework import serializers

from rest_flex_fields import split_levels


class FlexFieldsSerializerMixin(object):
    """
        A ModelSerializer that takes additional arguments for
        "fields", "omit" and "expand" in order to
        control which fields are displayed, and whether to replace simple
        values with complex, nested serializations.clean
    """

    expandable_fields = {}

    def __init__(self, *args, **kwargs):
        expand = list(kwargs.pop("expand", []))
        fields = list(kwargs.pop("fields", []))
        omit = list(kwargs.pop("omit", []))

        super(FlexFieldsSerializerMixin, self).__init__(*args, **kwargs)

        self.expanded_fields = []
        self._flex_fields_applied = False

        self._flex_options = {
            "expand": self._get_expand_input(expand),
            "fields": self._get_fields_input(fields),
            "omit": self._get_omit_input(omit),
        }

    def to_representation(self, *args, **kwargs):
        if self._flex_fields_applied is False:
            self.apply_flex_fields()
        return super().to_representation(*args, **kwargs)

    def apply_flex_fields(self):
        expand_fields, next_expand_fields = split_levels(self._flex_options["expand"])
        sparse_fields, next_sparse_fields = split_levels(self._flex_options["fields"])
        omit_fields, next_omit_fields = split_levels(self._flex_options["omit"])

        self._clean_fields(
            omit_fields, sparse_fields, next_omit_fields,
        )

        expanded_field_names = self._get_expanded_names(
            expand_fields, omit_fields, sparse_fields, next_omit_fields,
        )

        for name in expanded_field_names:
            self.expanded_fields.append(name)

            self.fields[name] = self._make_expanded_field_serializer(
                name, next_expand_fields, next_sparse_fields, next_omit_fields,
            )

        self._flex_fields_applied = True

    def _make_expanded_field_serializer(
        self, name, nested_expand, nested_fields, nested_omit
    ):
        """
        Returns an instance of the dynamically created nested serializer.
        """
        field_options = self._expandable_fields[name]

        if isinstance(field_options, tuple):
            serializer_class = field_options[0]
            settings = copy.deepcopy(field_options[1]) if len(field_options) > 1 else {}
        else:
            serializer_class = field_options
            settings = {}

        if name in nested_expand:
            settings["expand"] = nested_expand[name]

        if name in nested_fields:
            settings["fields"] = nested_fields[name]

        if name in nested_omit:
            settings["omit"] = nested_omit[name]

        if settings.get("source") == name:
            del settings["source"]

        if type(serializer_class) == str:
            serializer_class = self._import_serializer_class(serializer_class)

        return serializer_class(**settings)

    def _import_serializer_class(self, location):
        """
        Resolves a dot-notation string to serializer class.
        <app>.<SerializerName> will automatically be interpreted as:
        <app>.serializers.<SerializerName>
        """
        pieces = location.split(".")
        class_name = pieces.pop()

        if pieces[len(pieces) - 1] != "serializers":
            pieces.append("serializers")

        module = importlib.import_module(".".join(pieces))
        return getattr(module, class_name)

    def _clean_fields(self, omit_fields, sparse_fields, next_level_omits):
        """
            Remove fields that are found in omit list, and if sparse names
            are passed, remove any fields not found in that list.
        """
        sparse = len(sparse_fields) > 0
        to_remove = []

        if not sparse and len(omit_fields) == 0:
            return

        for field_name in self.fields:
            should_exist = self._should_field_exist(
                field_name, omit_fields, sparse_fields, next_level_omits
            )

            if not should_exist:
                to_remove.append(field_name)

        for remove_field in to_remove:
            self.fields.pop(remove_field)

    def _should_field_exist(
        self, field_name, omit_fields, sparse_fields, next_level_omits
    ):
        """
            Next level omits take form of:
            {
                'this_level_field': [field_to_omit_at_next_level]
            }
            We don't want to prematurely omit a field, eg "omit=house.rooms.kitchen"
            should not omit the entire house or all the rooms, just the kitchen.
        """
        if field_name in omit_fields and field_name not in next_level_omits:
            return False

        if len(sparse_fields) > 0 and field_name not in sparse_fields:
            return False

        return True

    def _get_expanded_names(
        self, expand_fields, omit_fields, sparse_fields, next_level_omits
    ):
        if len(expand_fields) == 0:
            return []

        if "~all" in expand_fields or "*" in expand_fields:
            expand_fields = self._expandable_fields.keys()

        accum = []

        for name in expand_fields:
            if name not in self._expandable_fields:
                continue

            if not self._should_field_exist(
                name, omit_fields, sparse_fields, next_level_omits
            ):
                continue

            accum.append(name)

        return accum

    @property
    def _expandable_fields(self) -> dict:
        """ It's more consistent with DRF to declare the expandable fields
            on the Meta class, however we need to support both places
            for legacy reasons. """
        if hasattr(self, "Meta") and hasattr(self.Meta, "expandable_fields"):
            return self.Meta.expandable_fields

        return self.expandable_fields

    @property
    def _can_access_request(self):
        """
        Can access current request object if all are true
        - The serializer is the root.
        - A request context was passed in.
        """
        if self.parent:
            return False

        if not hasattr(self, "context") or not self.context.get("request", None):
            return False

        return True

    def _get_omit_input(self, passed):
        if len(passed) > 0:
            return passed

        return self._parse_request_list_value("omit")

    def _get_fields_input(self, passed):
        if len(passed) > 0:
            return passed

        return self._parse_request_list_value("fields")

    def _parse_request_list_value(self, field):
        if not self._can_access_request:
            return []

        values = self.context["request"].query_params.getlist(field)
        if not values:
            values = self.context["request"].query_params.getlist("{}[]".format(field))

        if values and len(values) == 1:
            return values[0].split(",")
        return values or []

    def _get_expand_input(self, passed):
        """
            If expand value is explicitliy passed, just return it.
            If parsing from request, ensure that the value complies with
            the "permitted_expands" list passed into the context from the
            FlexFieldsMixin.
        """
        if len(passed) > 0:
            return passed

        if not self._can_access_request:
            return []

        expand = self._parse_request_list_value("expand")

        if "permitted_expands" in self.context:
            permitted_expands = self.context["permitted_expands"]

            if "~all" in expand or "*" in expand:
                return permitted_expands
            else:
                return list(set(expand) & set(permitted_expands))

        return expand


class FlexFieldsModelSerializer(FlexFieldsSerializerMixin, serializers.ModelSerializer):
    pass
