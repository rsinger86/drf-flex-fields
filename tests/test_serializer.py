import unittest

from rest_framework import serializers

from rest_flex_fields import FlexFieldsModelSerializer
from tests.testapp.models import Company, Person, Pet
from tests.testapp.serializers import PetSerializer


class MockRequest(object):

    def __init__(self, query_params={}, method='GET'):
        self.query_params = query_params
        self.method = method


class TestSerialize(unittest.TestCase):

    def test_basic_field_omit(self):
        pet = Pet(
            name='Garfield',
            toys='paper ball, string',
            species='cat',
            owner=Person(name='Fred')
        )

        expected_serializer_data = {
            'name': 'Garfield',
            'toys': 'paper ball, string'
        }

        serializer = PetSerializer(pet, omit=['species', 'owner'])
        self.assertEqual(serializer.data, expected_serializer_data)

        serializer = PetSerializer(pet, omit=(field for field in ('species', 'owner')))
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_nested_field_omit(self):
        pet = Pet(
            name='Garfield',
            toys='paper ball, string',
            species='cat',
            owner=Person(name='Fred', employer=Company(name='McDonalds'))
        )

        expected_serializer_data = {
            'name': 'Garfield',
            'toys': 'paper ball, string',
            'species': 'cat',
            'owner': {
                'hobbies': '',
                'employer': {
                   'name': 'McDonalds'
                }
            }
        }

        serializer = PetSerializer(
            pet,
            expand=['owner.employer'],
            omit=['owner.name', 'owner.employer.public']
        )
        self.assertEqual(serializer.data, expected_serializer_data)

        serializer = PetSerializer(
            pet,
            expand=(field for field in ('owner.employer',)),
            omit=(field for field in ('owner.name', 'owner.employer.public'))
        )
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_basic_field_include(self):
        pet = Pet(
            name='Garfield',
            toys='paper ball, string',
            species='cat',
            owner=Person(name='Fred')
        )

        expected_serializer_data = {
            'name': 'Garfield',
            'toys': 'paper ball, string'
        }

        serializer = PetSerializer(pet, fields=['name', 'toys'])
        self.assertEqual(serializer.data, expected_serializer_data)

        serializer = PetSerializer(pet, fields=(field for field in ('name', 'toys')))
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_nested_field_include(self):
        pet = Pet(
            name='Garfield',
            toys='paper ball, string',
            species='cat',
            owner=Person(name='Fred', employer=Company(name='McDonalds'))
        )

        expected_serializer_data = {
            'owner': {
                'employer': {
                    'name': 'McDonalds'
                }
            }
        }

        serializer = PetSerializer(pet, expand=['owner.employer'], fields=[
                                   'owner.employer.name'])
        self.assertEqual(serializer.data, expected_serializer_data)

        serializer = PetSerializer(pet, expand=(field for field in ('owner.employer',)),
                                    fields=(field for field in ('owner.employer.name',)))
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_basic_expand(self):
        pet = Pet(
            name='Garfield',
            toys='paper ball, string',
            species='cat',
            owner=Person(name='Fred', hobbies='sailing')
        )

        expected_serializer_data = {
            'name': 'Garfield',
            'toys': 'paper ball, string',
            'species': 'cat',
            'owner': {
                'name': 'Fred',
                'hobbies': 'sailing'
            }
        }

        serializer = PetSerializer(pet, expand=['owner'])
        self.assertEqual(serializer.data, expected_serializer_data)

        serializer = PetSerializer(pet, expand=(field for field in ('owner',)))
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_nested_expand(self):
        pet = Pet(
            name='Garfield',
            toys='paper ball, string',
            species='cat',
            owner=Person(name='Fred', hobbies='sailing',
                         employer=Company(name='McDonalds'))
        )

        expected_serializer_data = {
            'name': 'Garfield',
            'toys': 'paper ball, string',
            'species': 'cat',
            'owner': {
                'name': 'Fred',
                'hobbies': 'sailing',
                'employer': {
                    'public': False,
                    'name': 'McDonalds'
                }
            }
        }

        serializer = PetSerializer(pet, expand=['owner.employer'])
        self.assertEqual(serializer.data, expected_serializer_data)

        serializer = PetSerializer(pet, expand=(field for field in ('owner.employer',)))
        self.assertEqual(serializer.data, expected_serializer_data)

    def test_expand_from_request(self):
        pet = Pet(
            name='Garfield',
            toys='paper ball, string',
            species='cat',
            owner=Person(name='Fred', hobbies='sailing',
                         employer=Company(name='McDonalds'))
        )

        request = MockRequest(query_params={'expand': 'owner.employer'})
        serializer = PetSerializer(pet, context={'request': request})

        self.assertEqual(serializer.data, {
            'name': 'Garfield',
            'toys': 'paper ball, string',
            'species': 'cat',
            'owner': {
                'name': 'Fred',
                'hobbies': 'sailing',
                'employer': {
                    'public': False,
                    'name': 'McDonalds'
                }
            }
        })
