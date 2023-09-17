from rest_framework import serializers

class FlexSerializerMethodField(serializers.SerializerMethodField):
    def __init__(self, method_name=None, **kwargs):
        self.expand = kwargs.pop("expand", [])
        self.fields = kwargs.pop("fields", [])
        self.omit = kwargs.pop("omit", [])
        super().__init__(method_name, **kwargs)

    def to_representation(self, value):
        method = getattr(self.parent, self.method_name)
        return method(value, self.fields, self.expand, self.omit)
