#!/usr/bin/env python
from distutils.core import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.txt'), encoding='utf-8') as f:
      long_description = f.read()


setup(name='drf-flex-fields',
      version='0.1.8',
      description='Flexible, dynamic fields and nested models for Django REST Framework serializers.',
      author='Robert Singer',
      author_email='robertgsinger@gmail.com',
      packages=['rest_flex_fields'],
      url='https://github.com/rsinger86/drf-flex-fields',
      license='MIT',
      keywords='django rest api dynamic fields',
      long_description=long_description,
)