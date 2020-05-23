#!/usr/bin/env python
from setuptools import setup
from codecs import open


def readme():
    with open("README.md", "r") as infile:
        return infile.read()


classifiers = [
    # Pick your license as you wish (should match "license" above)
    "License :: OSI Approved :: MIT License",
    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
]
setup(
    name="drf-flex-fields",
    version="0.8.5",
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
