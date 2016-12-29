import unittest
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers
from testapp.models import Pet, Person, Company


class TestFlexFieldSerializer(unittest.TestCase):

    def setUp(self):
        class _CompanySerializer(FlexFieldsModelSerializer):
            class Meta:
                model = Company  
                fields = ['name', 'public']


        class _PersonSerializer(FlexFieldsModelSerializer):
            class Meta:
                model = Person  
                fields = ['name', 'hobbies']

            expandable_fields = {
                'employer': (_CompanySerializer, {'source': 'employer'})
            }

        class _PetSerializer(FlexFieldsModelSerializer):
            class Meta:
                model = Pet  
                fields = ['name', 'toys', 'species']
        
            expandable_fields = {
                'owner': (_PersonSerializer, {'source': 'owner'})
            }

        self.PersonSerializer = _PersonSerializer
        self.PetSerializer = _PetSerializer
        self.CompanySerializer = _CompanySerializer


    def test_basic_field_include(self):
        pet = Pet(
            name='Remy', 
            toys='paper ball, string', 
            species='cat',
            owner=Person(name='Fred')
        )

        serializer = self.PetSerializer(pet, include_fields=['name', 'toys'])
        self.assertEqual(serializer.data['toys'], 'paper ball, string')
        self.assertEqual(serializer.data['name'], 'Remy')


    def test_basic_field_exclude(self):
        pet = Pet(
            name='Remy', 
            toys='paper ball, string', 
            species='cat',
            owner=Person(name='Fred')
        )

        serializer = self.PetSerializer(pet, exclude_fields=['species'])
        self.assertEqual(serializer.data, {
            'name' : 'Remy',
            'toys' : 'paper ball, string'
        })


    def test_nested_field_include(self):
        pet = Pet(
            name='Remy', 
            toys='paper ball, string', 
            species='cat',
            owner=Person(name='Fred', employer=Company(name='McDonalds'))
        )

        serializer = self.PetSerializer(pet, expand_fields=['owner.employer'], include_fields=['owner.employer.name'])
        self.assertEqual(serializer.data, {
            'owner' : {
                'employer' : {
                    'name' : 'McDonalds'
                }    
            }
        })


    def test_nested_field_exclude(self):
        pet = Pet(
            name='Remy', 
            toys='paper ball, string', 
            species='cat',
            owner=Person(
                name='Fred', 
                hobbies='sailing',
                employer=Company(name='McDonalds')
            )
        )

        serializer = self.PetSerializer(
            pet, 
            expand_fields=['owner.employer'], 
            exclude_fields=['toys', 'owner.name', 'owner.employer.public']
        )

        self.assertEqual(serializer.data, {
            'name' : 'Remy',
           #'toys' : 'paper ball, string',
            'species' : 'cat',
            'owner' : {
               #'name' : 'Fred',
                'hobbies' : 'sailing',
                'employer' : {
                   #'public' : False,
                    'name' : 'McDonalds'
                }    
            }
        })


    def test_basic_expand(self):
        pass