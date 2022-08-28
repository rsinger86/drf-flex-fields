from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=30)
    public = models.BooleanField(default=False)


class PetStore(models.Model):
    name = models.CharField(max_length=30)


class Person(models.Model):
    name = models.CharField(max_length=30)
    hobbies = models.CharField(max_length=30)
    employer = models.ForeignKey(Company, on_delete=models.CASCADE)


class Pet(models.Model):
    name = models.CharField(max_length=30)
    toys = models.CharField(max_length=30)
    species = models.CharField(max_length=30)
    owner = models.ForeignKey(Person, on_delete=models.CASCADE)
    sold_from = models.ForeignKey(PetStore, null=True, on_delete=models.CASCADE)
    diet = models.CharField(max_length=200)


class TaggedItem(models.Model):
    tag = models.SlugField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')