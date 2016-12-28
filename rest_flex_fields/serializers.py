from rest_framework import serializers
import importlib


class FlexFieldsModelSerializer(serializers.ModelSerializer):
    """
        A ModelSerializer that uses the expand argument to figure out
        how to dynamically expand related fields.
    """
    expandable_fields = {}

    def __init__(self, *args, **kwargs):
        expand_field_names = self._get_dynamic_setting(kwargs, 'expand_fields')
        include_field_names = self._get_dynamic_setting(kwargs, 'include_fields')
        exclude_field_names = self._get_dynamic_setting(kwargs, 'exclude_fields')

        expand_field_names, next_expand_field_names = self._split_levels(expand_field_names)
        include_field_names, next_include_field_names = self._split_levels(include_field_names)
        exclude_field_names, next_exclude_field_names = self._split_levels(exclude_field_names)

        self._clean_fields(include_field_names, exclude_field_names)
        
        if '~all' in expand_field_names:
            expand_field_names = self.expandable_fields.keys()
        
        for name in expand_field_names:
            if name not in self.expandable_fields:
                continue

            self.fields[name] = self._make_expanded_field_serializer(
                name, next_expand_field_names, next_include_field_names, next_exclude_field_names
            )
        
        super(FlexFieldsModelSerializer, self).__init__(*args, **kwargs)
        

    def _make_expanded_field_serializer(self, name, nested_expands, nested_includes, nested_excludes):
        field_options = self.expandable_fields[name]
        serializer_class = field_options[0]
        serializer_settings = field_options[1]
        
        if name in nested_expands:
            serializer_settings['expand_fields'] = nested_expands[name]

        if name in nested_includes:
            serializer_settings['include_fields'] = nested_includes[name]

        if name in nested_excludes:
            serializer_settings['exclude_fields'] = nested_excludes[name]

        if serializer_settings.get('source') == name:
            del serializer_settings['source']
            
        if type(serializer_class) == str:
            serializer_class = self._import_serializer_class(serializer_class) 
        
        return serializer_class(**serializer_settings)

    
    def _import_serializer_class(self, location):
        pieces = location.split('.')
        class_name = pieces.pop()
        if pieces[ len(pieces)-1 ] != 'serializers':
            pieces.append('serializers')

        module = importlib.import_module( '.'.join(pieces) ) 
        return getattr(module, class_name)


    def _clean_fields(self, include_fields, exclude_fields):
        if include_fields:
            allowed = set(include_fields)
            existing = set(self.fields.keys())

            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if exclude_fields:
            for exclude_field in exclude_fields:
                self.fields.pop(exclude_field)


    def _split_levels(self, fields):
        """
            Convert ['a', 'a.b', 'a.d', 'c']
            into first_level_fields - ['a', 'c'] and
            next_level_fields {'a': ['b', 'd']}
        """
        first_level_fields = []
        next_level_fields = {}

        if not fields:
            return first_level_fields, next_level_fields

        if not isinstance(fields, list):
            fields = [a.strip() for a in fields.split(',') if a.strip()]
        for e in fields:
            if '.' in e:
                first_level, next_level = e.split('.', 1)
                first_level_fields.append(first_level)
                next_level_fields.setdefault(first_level, []).append(next_level)
            else:
                first_level_fields.append(e)
                
        first_level_fields = list(set(first_level_fields))
        return first_level_fields, next_level_fields

    
    def _get_dynamic_setting(self, passed_settings, prop):
        """ 
            Returns value of dynamic setting.

            The value can be set in one of two places:
            (a) The originating request's GET params; it is then defined on the serializer class 
            (b) Manually when a nested serializer field is defined; it is then passed in the serializer class constructor
        """
        if hasattr(self, prop):
            return getattr(self, prop)
        
        return passed_settings.pop(prop, None)