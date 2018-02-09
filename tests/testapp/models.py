from __future__ import unicode_literals
from django.db import models



class Company(models.Model):
    name = models.CharField(max_length=30)
    public = models.BooleanField(default=False)



class Person(models.Model):
    name = models.CharField(max_length=30)
    hobbies = models.CharField(max_length=30)
    employer = models.ForeignKey(Company, on_delete=models.CASCADE)



class Pet(models.Model):
    name = models.CharField(max_length=30)
    toys = models.CharField(max_length=30)
    species = models.CharField(max_length=30)
    owner = models.ForeignKey(Person, on_delete=models.CASCADE)