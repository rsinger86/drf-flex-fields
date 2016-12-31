#!/usr/bin/env python
from distutils.core import setup

try:
      import pypandoc
      long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
      long_description = open('README.md').read()


setup(name='drf-flex-fields',
      version='0.1.2',
      description='Flexible, dynamic fields and nested models for Django REST Framework serializers.',
      author='Robert Singer',
      author_email='robertgsinger@gmail.com',
      packages=['rest_flex_fields'],
      long_description=long_description,
)