#!/usr/bin/env python
from setuptools import setup
from codecs import open


def readme():
    with open("README.md", "r") as infile:
        return infile.read()


classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
]
setup(
    name="drf-flex-fields",
    version="1.0.2",
    description="Flexible, dynamic fields and nested resources for Django REST Framework serializers.",
    author="Robert Singer",
    author_email="robertgsinger@gmail.com",
    packages=["rest_flex_fields"],
    url="https://github.com/rsinger86/drf-flex-fields",
    license="MIT",
    keywords="django rest api dynamic fields",
    long_description=readme(),
    classifiers=classifiers,
    long_description_content_type="text/markdown",
)
