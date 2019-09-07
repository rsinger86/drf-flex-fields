#!/usr/bin/env python
from distutils.core import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.txt"), encoding="utf-8") as f:
    long_description = f.read()


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
]
setup(
    name="drf-flex-fields",
    version="0.6.0",
    description="Flexible, dynamic fields and nested resources for Django REST Framework serializers.",
    author="Robert Singer",
    author_email="robertgsinger@gmail.com",
    packages=["rest_flex_fields"],
    url="https://github.com/rsinger86/drf-flex-fields",
    license="MIT",
    keywords="django rest api dynamic fields",
    long_description=long_description,
    classifiers=classifiers,
)
