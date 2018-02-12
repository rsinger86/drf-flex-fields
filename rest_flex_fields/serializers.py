import importlib
import copy
from rest_framework import serializers
from rest_flex_fields import split_levels



class FlexFieldsModelSerializer(serializers.ModelSerializer):
    """
        A ModelSerializer that takes additional arguments for 
        "fields" and "include" in order to
        control which fields are displayed, and whether to replace simple values with
        complex, nested serializations.
    """
    expandable_fields = {}

    def __init__(self, *args, **kwargs):
        self.expanded_fields = []

        passed = { 
            'expand' : kwargs.pop('expand', None), 
            'fields': kwargs.pop('fields', None) 
        }

        super(FlexFieldsModelSerializer, self).__init__(*args, **kwargs)
        expand = self._get_expand_input(passed)
        fields = self._get_fields_input(passed)
        expand_field_names, next_expand_field_names = split_levels(expand)
        sparse_field_names, next_sparse_field_names = split_levels(fields)
        expandable_fields_names = self._get_expandable_names(sparse_field_names)

        if '~all' in expand_field_names:
            expand_field_names = self.expandable_fields.keys()
        
        for name in expand_field_names:
            if name not in expandable_fields_names:
                continue
            
            self.expanded_fields.append(name)

            self.fields[name] = self._make_expanded_field_serializer(
                name, next_expand_field_names, next_sparse_field_names
            )
        

    def _make_expanded_field_serializer(self, name, nested_expands, nested_includes):
        """
        Returns an instance of the dynamically created nested serializer. 
        """
        field_options = self.expandable_fields[name]
        serializer_class = field_options[0]
        serializer_settings = copy.deepcopy(field_options[1])
        
        if name in nested_expands:
            serializer_settings['expand'] = nested_expands[name]

        if name in nested_includes:
            serializer_settings['fields'] = nested_includes[name]

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
        if pieces[ len(pieces)-1 ] != 'serializers':
            pieces.append('serializers')

        module = importlib.import_module( '.'.join(pieces) ) 
        return getattr(module, class_name)


    def _get_expandable_names(self, sparse_field_names):
        if not sparse_field_names:
            return self.expandable_fields.keys()
            
        allowed_field_names = set(sparse_field_names)
        field_names = set(self.fields.keys())
        expandable_field_names = set(self.expandable_fields.keys())

        for field_name in field_names - allowed_field_names:
            self.fields.pop(field_name)
        
        return list(expandable_field_names & allowed_field_names)


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
        
        if not hasattr(self, 'context') or 'request' not in self.context:
            return False 
        
        return self.context['request'].method == 'GET'


    def _get_fields_input(self, passed_settings):
        value = passed_settings.get('fields')

        if value:
            return value

        if not self._can_access_request:
            return None

        fields = self.context['request'].query_params.get('fields')
        return fields.split(',') if fields else None


    def _get_expand_input(self, passed_settings):
        """
            If not expandable (ViewSet list method set this to false),
            check to see if there are any fields that we are forcing 
            to be expanded (from permit_list_expands).
        """
        value = passed_settings.get('expand')
        
        if value:
            return value

        if not self._can_access_request:
            return None

        if self.context.get('expandable') is False:
            force_expand = self.context.get('force_expand', [])
            if len(force_expand) > 0:
                return force_expand

            return None
        
        expand = self.context['request'].query_params.get('expand')
        return expand.split(',') if expand else None