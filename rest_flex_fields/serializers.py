import copy
import importlib

from rest_framework import serializers

from rest_flex_fields import split_levels


class FlexFieldsSerializerMixin(object):
    """
        A ModelSerializer that takes additional arguments for
        "fields", "omit" and "expand" in order to
        control which fields are displayed, and whether to replace simple
        values with complex, nested serializations.
    """
    expandable_fields = {}

    def __init__(self, *args, **kwargs):
        self.expanded_fields = []

        passed = {
            'expand': kwargs.pop('expand', []),
            'fields': kwargs.pop('fields', []),
            'omit': kwargs.pop('omit', [])
        }

        super(FlexFieldsSerializerMixin, self).__init__(*args, **kwargs)
        expand = self._get_expand_input(passed)
        fields = self._get_fields_input(passed)
        omit = self._get_omit_input(passed)

        expand_field_names, next_expand_field_names = split_levels(expand)
        sparse_field_names, next_sparse_field_names = split_levels(fields)
        omit_field_names, next_omit_field_names = split_levels(omit)

        self._clean_fields(omit_field_names, sparse_field_names)

        expanded_field_names = self._get_expanded_names(
            expand_field_names,
            sparse_field_names,
            omit_field_names
        )

        for name in expanded_field_names:
            self.expanded_fields.append(name)

            self.fields[name] = self._make_expanded_field_serializer(
                name,
                next_expand_field_names,
                next_sparse_field_names,
                next_omit_field_names
            )

    def _make_expanded_field_serializer(self, name, nested_expand, nested_fields, nested_omit):
        """
        Returns an instance of the dynamically created nested serializer.
        """
        field_options = self.expandable_fields[name]
        serializer_class = field_options[0]
        serializer_settings = copy.deepcopy(field_options[1])

        if name in nested_expand:
            serializer_settings['expand'] = nested_expand[name]

        if name in nested_fields:
            serializer_settings['fields'] = nested_fields[name]

        if name in nested_omit:
            serializer_settings['omit'] = nested_omit[name]

        if serializer_settings.get('source') == name:
            del serializer_settings['source']

        if type(serializer_class) == str:
            serializer_class = self._import_serializer_class(serializer_class)

        return serializer_class(**serializer_settings)

    def _import_serializer_class(self, location):
        """
        Resolves a dot-notation string to serializer class.
        <app>.<SerializerName> will automatically be interpreted as:
        <app>.serializers.<SerializerName>
        """
        pieces = location.split('.')
        class_name = pieces.pop()

        if pieces[len(pieces)-1] != 'serializers':
            pieces.append('serializers')

        module = importlib.import_module('.'.join(pieces))
        return getattr(module, class_name)

    def _clean_fields(self, omit_names, sparse_names):
        """
            Remove fields that are found in omit list, and if sparse names
            are passed, remove any fields not found in that list.
        """
        sparse = len(sparse_names) > 0
        to_remove = []

        if not sparse and len(omit_names) == 0:
            return

        for field_name in self.fields:
            if field_name in omit_names and field_name in self.fields:
                to_remove.append(field_name)
            elif sparse and field_name not in sparse_names and field_name in self.fields:
                to_remove.append(field_name)

        for remove_field in to_remove:
            self.fields.pop(remove_field)

    def _get_expanded_names(self,
                            expand_field_names,
                            sparse_field_names,
                            omit_field_names):
        if len(expand_field_names) == 0:
            return []

        if '~all' or '*' in expand_field_names:
            expand_field_names = self.expandable_fields.keys()

        accum = []

        for name in expand_field_names:
            if name not in self.expandable_fields:
                continue

            if name in omit_field_names:
                continue

            if len(sparse_field_names) > 0 and name not in sparse_field_names:
                continue

            accum.append(name)

        return accum

    @property
    def _can_access_request(self):
        """
        Can access current request object if all are true
        - The serializer is the root.
        - A request context was passed in.
        - The request method is GET.
        """
        if self.parent:
            return False

        if not hasattr(self, 'context') or not self.context.get('request', None):
            return False

        return self.context['request'].method == 'GET'

    def _get_omit_input(self, passed_settings):
        value = passed_settings.get('omit')

        if len(value) > 0:
            return value

        if not self._can_access_request:
            return []

        omit = self.context['request'].query_params.get('omit')
        return omit.split(',') if omit else []

    def _get_fields_input(self, passed_settings):
        value = passed_settings.get('fields')

        if len(value) > 0:
            return value

        if not self._can_access_request:
            return []

        fields = self.context['request'].query_params.get('fields')
        return fields.split(',') if fields else []

    def _get_expand_input(self, passed_settings):
        """
            If not expandable (ViewSet list method set this to false),
            check to see if there are any fields that we are forcing
            to be expanded (from permit_list_expands).
        """
        value = passed_settings.get('expand')

        if len(value) > 0:
            return value

        if not self._can_access_request:
            return []

        if self.context.get('expandable') is False:
            force_expand = self.context.get('force_expand', [])
            if len(force_expand) > 0:
                return force_expand

            return []

        expand = self.context['request'].query_params.get('expand')
        return expand.split(',') if expand else []


class FlexFieldsModelSerializer(FlexFieldsSerializerMixin,
                                serializers.ModelSerializer):
    pass
