import unittest
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers
from testapp.models import Pet


class TestFlexFieldSerializer(unittest.TestCase):

    def test(self):
        class PetSerializer(FlexFieldsModelSerializer):
            class Meta:
                model = Pet  
                fields = ['name', 'toys', 'species']

        Serializer = PetSerializer
        pet = Pet(name='Remy')
        serializer = Serializer(pet)
        # print(serializer.data)
        self.assertEqual(1,1)
