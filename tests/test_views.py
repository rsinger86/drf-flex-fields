from django.urls import reverse
from rest_framework.test import APITestCase
from tests.testapp.models import Pet, Person, Company



class PetViewTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name='McDonalds')

        self.person = Person.objects.create(
            name='Fred', 
            hobbies='sailing', 
            employer=self.company
        )

        self.pet = Pet.objects.create(
            name='Garfield', 
            toys='paper ball, string', 
            species='cat',
            owner=self.person
        )


    def tearDown(self):
        Company.objects.all().delete()
        Person.objects.all().delete()
        Pet.objects.all().delete()


    def test_retrieve_expanded(self):
        url = reverse('pet-detail', args=[self.pet.id])
        response = self.client.get(url+'?expand=owner',format='json')

        self.assertEqual(response.data, {
            'name' : 'Garfield',
            'toys' : 'paper ball, string',
            'species' : 'cat',
            'owner' : {
                'name' : 'Fred',
                'hobbies' : 'sailing' 
            }
        })


    def test_retrieve_sparse(self):
        url = reverse('pet-detail', args=[self.pet.id])
        response = self.client.get(url+'?fields=name,species',format='json')

        self.assertEqual(response.data, {
            'name' : 'Garfield',
            'species' : 'cat'
        })


    def test_retrieve_sparse_and_deep_expanded(self):
        url = reverse('pet-detail', args=[self.pet.id])
        url = url+'?fields=owner&expand=owner.employer'
        response = self.client.get(url, format='json')

        self.assertEqual(response.data, {
            'owner' : {
                'name' : 'Fred',
                'hobbies' : 'sailing',
                'employer' : {
                    'public' : False,
                    'name' : 'McDonalds'
                }    
            }
        })


    def test_list_expanded(self):
        url = reverse('pet-list')
        url = url+'?expand=owner'
        response = self.client.get(url, format='json')

        self.assertEqual(response.data[0], {
            'name' : 'Garfield',
            'toys' : 'paper ball, string',
            'species' : 'cat',
            'owner' : {
                'name' : 'Fred',
                'hobbies' : 'sailing' 
            }
        })