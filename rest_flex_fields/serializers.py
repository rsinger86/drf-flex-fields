from rest_framework import serializers
import importlib


class FlexFieldsModelSerializer(serializers.ModelSerializer):
    """
        A ModelSerializer that takes additional arguments for 
        expand_fields, include_fields and exclude fields in order to
        control which fields are displayed, and whether to replace simple values with
        embedded serializations.
    """
    expandable_fields = {}

    def __init__(self, *args, **kwargs):
        expand_field_names = self._get_dynamic_setting(kwargs, 'expand')
        include_field_names = self._get_dynamic_setting(kwargs, {'class_property': 'include_fields', 'kwargs': 'fields'})
        expand_field_names, next_expand_field_names = self._split_levels(expand_field_names)
        include_field_names, next_include_field_names = self._split_levels(include_field_names)
        self._expandable = self.expandable_fields.keys()

        # Instantiate the superclass normally
        super(FlexFieldsModelSerializer, self).__init__(*args, **kwargs)

        self._clean_fields(include_field_names)

        if '~all' in expand_field_names:
            expand_field_names = self.expandable_fields.keys()
        
        for name in expand_field_names:
            if name not in self._expandable:
                continue
            
            self.fields[name] = self._make_expanded_field_serializer(
                name, next_expand_field_names, next_include_field_names
            )
        

    def _make_expanded_field_serializer(self, name, nested_expands, nested_includes):
        """
        Returns an instance of the dynamically created embedded serializer. 
        """
        field_options = self.expandable_fields[name]
        serializer_class = field_options[0]
        serializer_settings = field_options[1]
        
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
        Resolves dot-notation string reference to serializer class and returns actual class.

        <app>.<SerializerName> will automatically be interpreted as <app>.serializers.<SerializerName>
        """
        pieces = location.split('.')
        class_name = pieces.pop()
        if pieces[ len(pieces)-1 ] != 'serializers':
            pieces.append('serializers')

        module = importlib.import_module( '.'.join(pieces) ) 
        return getattr(module, class_name)



    def _clean_fields(self, include_fields):
        if include_fields:
            allowed_fields = set(include_fields)
            existing_fields = set(self.fields.keys())
            existing_expandable_fields = set(self.expandable_fields.keys())

            for field_name in existing_fields - allowed_fields:
                self.fields.pop(field_name)
            
            self._expandable = list( existing_expandable_fields & allowed_fields )
  


    def _split_levels(self, fields):
        """
            Convert dot-notation such as ['a', 'a.b', 'a.d', 'c'] into current-level fields ['a', 'c'] 
            and next-level fields {'a': ['b', 'd']}.
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

    
    def _get_dynamic_setting(self, passed_settings, source):
        """ 
            Returns value of dynamic setting.

            The value can be set in one of two places:
            (a) The originating request's GET params; it is then defined on the serializer class 
            (b) Manually when a nested serializer field is defined; it is then passed in the serializer class constructor
        """
        if isinstance(source, dict):
            if hasattr(self, source['class_property']):
                return getattr(self, source['class_property'])
            
            return passed_settings.pop(source['kwargs'], None)
        else:
            if hasattr(self, source):
                return getattr(self, source)
            
            return passed_settings.pop(source, None)