""" 
    This class helps provide control over which fields can be expanded when a
    collection is requested via the list method.
"""
from fnmatch import fnmatch
from rest_framework import viewsets


class FlexFieldsMixin(object):
    permit_list_expands = []
    _expandable = True
    _force_expand = []

    def list(self, request, *args, **kwargs):
        """
            Prevent expansion by default; add fields to "permit_list_expands"
            to whitelist particular fields.
        """
        self._expandable = False
        expand = request.query_params.get('expand')

        if len(self.permit_list_expands) > 0 and expand:
            if expand == '*':
                self._force_expand = self.permit_list_expands
            else:
                self._force_expand = [field.strip() for field in expand.split(',') if
                                      any(fnmatch(field.strip(), permit_field) for permit_field in self.permit_list_expands)]

        return super(FlexFieldsMixin, self).list(request, *args, **kwargs)

    def create_serializer(self, serializer_class, *args, **kwargs):
        return serializer_class(*args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return self.create_serializer(serializer_class, *args, **kwargs)

    def get_serializer_context(self):
        default_context = super(FlexFieldsMixin, self).get_serializer_context()
        default_context['expandable'] = self._expandable
        default_context['force_expand'] = self._force_expand
        return default_context

    def get_queryset(self):
        queryset = super().get_queryset()
        expand = self.request.query_params.get('expand')

        if not expand:
            return queryset

        expand_fields = self.get_serializer_class().expandable_fields.keys() if expand == '*' else set([field.strip() for field in expand.split(',')])
        valid_expand_fields = expand_fields if self._expandable else set(expand_fields) & set(self._force_expand)

        for field in valid_expand_fields:
            queryset = self.expand_field(field, queryset)

        return queryset

    def expand_field(self, field, queryset):
        return queryset


class FlexFieldsModelViewSet(FlexFieldsMixin, viewsets.ModelViewSet):
    pass
