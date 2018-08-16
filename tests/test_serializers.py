import unittest
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers
from tests.testapp.models import Pet, Person, Company
from tests.testapp.serializers import PetSerializer



class MockRequest(object):

    def __init__(self, query_params={}, method='GET'):
        self.query_params = query_params
        self.method  = method 

    

class TestFlexFieldSerializer(unittest.TestCase):

    def test_basic_field_include(self):
        pet = Pet(
            name='Garfield', 
            toys='paper ball, string', 
            species='cat',
            owner=Person(name='Fred')
        )

        serializer = PetSerializer(pet, fields=['name', 'toys'])
        self.assertEqual(serializer.data, {
            'name' : 'Garfield',
            'toys' : 'paper ball, string'
        })


    def test_nested_field_include(self):
        pet = Pet(
            name='Garfield', 
            toys='paper ball, string', 
            species='cat',
            owner=Person(name='Fred', employer=Company(name='McDonalds'))
        )

        serializer = PetSerializer(pet, expand=['owner.employer'], fields=['owner.employer.name'])
        self.assertEqual(serializer.data, {
            'owner' : {
                'employer' : {
                    'name' : 'McDonalds'
                }    
            }
        })

    def test_basic_field_omit(self):
        pet = Pet(
            name='Garfield', 
            toys='paper ball, string', 
            species='cat',
            owner=Person(name='Fred')
        )

        serializer = PetSerializer(pet, exclude=['species', 'owner'])
        self.assertEqual(serializer.data, {
            'name' : 'Garfield',
            'toys' : 'paper ball, string'
        })


    def test_nested_field_omit(self):
        pet = Pet(
            name='Garfield', 
            toys='paper ball, string', 
            species='cat',
            owner=Person(name='Fred', employer=Company(name='McDonalds'))
        )

        serializer = PetSerializer(pet, expand=['owner.employer'], exclude=['species', 'owner.hobbies', 'owner.employer.public'])
        self.assertEqual(serializer.data, {
            'name' : 'Garfield',
            'toys' : 'paper ball, string',
            'owner' : {
                'name' : 'Fred',
                'employer' : {
                    'name' : 'McDonalds'
                }    
            }
        })


    def test_basic_expand(self):
        pet = Pet(
            name='Garfield', 
            toys='paper ball, string', 
            species='cat',
            owner=Person(name='Fred', hobbies='sailing')
        )

        serializer = PetSerializer(pet, expand=['owner'])
        self.assertEqual(serializer.data, {
            'name' : 'Garfield',
            'toys' : 'paper ball, string',
            'species' : 'cat',
            'owner' : {
                'name' : 'Fred',
                'hobbies' : 'sailing' 
            }
        })


    def test_nested_expand(self):
        pet = Pet(
            name='Garfield', 
            toys='paper ball, string', 
            species='cat',
            owner=Person(name='Fred', hobbies='sailing', employer=Company(name='McDonalds'))
        )

        serializer = PetSerializer(pet, expand=['owner.employer'])
        self.assertEqual(serializer.data, {
            'name' : 'Garfield',
            'toys' : 'paper ball, string',
            'species' : 'cat',
            'owner' : {
                'name' : 'Fred',
                'hobbies' : 'sailing',
                'employer' : {
                    'public' : False,
                    'name' : 'McDonalds'
                }    
            }
        })


    def test_expand_from_request(self):
        pet = Pet(
            name='Garfield', 
            toys='paper ball, string', 
            species='cat',
            owner=Person(name='Fred', hobbies='sailing', employer=Company(name='McDonalds'))
        )

        request = MockRequest(query_params={'expand': 'owner.employer'})
        serializer = PetSerializer(pet, context={'request': request})

        self.assertEqual(serializer.data, {
            'name' : 'Garfield',
            'toys' : 'paper ball, string',
            'species' : 'cat',
            'owner' : {
                'name' : 'Fred',
                'hobbies' : 'sailing',
                'employer' : {
                    'public' : False,
                    'name' : 'McDonalds'
                }    
            }
        })