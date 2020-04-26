# Django REST - FlexFields

[![Package version](https://badge.fury.io/py/drf-flex-fields.svg)](https://pypi.python.org/pypi/drf-flex-fields)
[![Python versions](https://img.shields.io/pypi/status/drf-flex-fields.svg)](https://img.shields.io/pypi/status/django-lifecycle.svg/)

Flexible, dynamic fields and nested models for Django REST Framework serializers.

# Overview

FlexFields (DRF-FF) for [Django REST Framework](https://django-rest-framework.org) is a package designed to provide a common baseline of functionality for dynamically setting fields and nested models within DRF serializers. This package is designed for simplicity, with minimal magic and entanglement with DRF's foundational classes.

Key benefits:
* Easily set up fields that be expanded to their fully serialized counterparts via query parameters (`users/?expand=organization,friends`)
* Select a subset of fields by either:
  * specifying which ones should be included (`users/?fields=id,first_name`)
  * specifying which ones should be excluded (`users/?omit=id,first_name`)
* Use dot notation to dynamically modify fields at arbitrary depths (`users/?expand=organization.owner.roles`)
* Flexible API - options can also be passed directly to a serializer: `UserSerializer(obj, expand=['organization'])`

# Quick Start

```python
from rest_flex_fields import FlexFieldsModelSerializer

class StateSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name')

class CountrySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name', 'population', 'states')
        expandable_fields = {
          'states': (StateSerializer, {'many': True})
        }

class PersonSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Person
        fields = ('id', 'name', 'country', 'occupation')
        expandable_fields = {'country': CountrySerializer}
```

```
GET /people/142/
```
```json
{
  "id": 142,
  "name": "Jim Halpert",
  "country": 1
}
```

```
GET /people/142/?expand=country.states
```
```json
{
  "id": 142,
  "name": "Jim Halpert",
  "country": {
    "id": 1,
    "name": "United States",
    "states": [
      {
        "id": 23,
        "name": "Ohio"
      },
      {
        "id": 2,
        "name": "Pennsylvania"
      }
    ]
  }
}
```
# Table of Contents:

- [Setup](#setup)
- [Usage](#usage)
  * [Dynamic field expansion](#dynamic-field-expansion)
  * [Deferred fields](#deferred-fields)
  * [Deep, nested Expansion](#deep-nested-expansion)
  * [Field expansion on "list" views](#list-views)
  * [Expanding a "many" relationship](#expanding-many)
  * [Dynamically setting fields (sparse fields)](#dynamically-setting-fields)
  * [Reference serializer as a string (lazy evaluation)](#lazy-ref)
  * [Increase re-usability of serializers](#increased-reuse)
- [Serializer Options - Overview](#serializer-options)
- [Advanced](#advanced)
  * [Serializer introspection](#serializer-introspection)
  * [Use "~all" to expand all available fields](#use-all)
  * [Combining sparse and expanded fields](#combining-sparse-and-expanded)
  * [Query optimization (experimental)](#query-optimization-experimental)
- [Change Log](#changelog)
- [Testing](#testing)
- [License](#license)

# Setup

First install:
```
pip install drf-flex-fields
```

Then have your serializers subclass `FlexFieldsModelSerializer`:
```python
from rest_flex_fields import FlexFieldsModelSerializer

class StateSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name')

class CountrySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name', 'population', 'states')
        expandable_fields = {
          'states': (StateSerializer, {'many': True})
        }
```

Alternatively, you can add the `FlexFieldsSerializerMixin` mixin to a model serializer.

# Usage

## Dynamic Field Expansion

To define expandable fields, add an `expandable_fields` dictionary to your serializer's `Meta` class. Key the dictionary with the name of the field that you want to dynamically expand, and set its value to either the expanded serializer or a tuple where the first element is the serializer and the second is a dictionary of options that will be used to instantiate the serializer.

```python
class CountrySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Country
        fields = ['name', 'population']


class PersonSerializer(FlexFieldsModelSerializer):
    country = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Person
        fields = ['id', 'name', 'country', 'occupation']

        expandable_fields = {
            'country': CountrySerializer
        }
```

If the default serialized response is the following:
```json
{
  "id" : 13322,
  "name" : "John Doe",
  "country" : 12,
  "occupation" : "Programmer",
}
```
When you do a `GET /person/13322?expand=country`, the response will change to:

```json
{
  "id" : 13322,
  "name" : "John Doe",
  "country" : {
    "name" : "United States",
    "population": 330000000
  },
  "occupation" : "Programmer",
}
```

## Deferred Fields
Alternatively, you could treat ```country``` as a "deferred" field by not defining it among the default fields. To make a field deferred, only define it within the serializer's ```expandable_fields```.

## Deep, Nested Expansion
Let's say you add ```StateSerializer``` as a serializer nested inside the country serializer above:

```python
class StateSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = State
        fields = ['name', 'population']


class CountrySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Country
        fields = ['name', 'population']

        expandable_fields = {
            'states': (StateSerializer, {'many': True})
        }

class PersonSerializer(FlexFieldsModelSerializer):
    country = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Person
        fields = ['id', 'name', 'country', 'occupation']

        expandable_fields = {
            'country': CountrySerializer
        }
```

Your default serialized response might be the following for `person` and `country`, respectively:
```json
{
  "id" : 13322,
  "name" : "John Doe",
  "country" : 12,
  "occupation" : "Programmer",
}

{
  "id" : 12,
  "name" : "United States",
  "states" : "http://www.api.com/countries/12/states"
}
```
But if you do a ```GET /person/13322?expand=country.states```, it would be:
```json
{
  "id" : 13322,
  "name" : "John Doe",
  "occupation" : "Programmer",
  "country" : {
    "id" : 12,
    "name" : "United States",
    "states" : [
      {
        "name" : "Ohio",
        "population": 11000000
      }
    ]
  }
}
```
Please be kind to your database, as this could incur many additional queries. Though, you can mitigate this impact through judicious use of ```prefetch_related``` and ```select_related``` when defining the queryset for your viewset.

## Field Expansion on "List" Views <a id="list-views"></a>

If you request many objects, expanding fields could lead to many additional database queries. Subclass `FlexFieldsModelViewSet` if you want to prevent expanding fields by default when calling a ViewSet's `list` method. Place those fields that you would like to expand in a `permit_list_expands` property on the ViewSet:

```python
from drf_flex_fields import is_expanded

class PersonViewSet(FlexFieldsModelViewSet):
    permit_list_expands = ['employer']
    serializer_class = PersonSerializer

    def get_queryset(self):
        queryset = models.Person.objects.all()
        if is_expanded(self.request, 'employer'):
            queryset = queryset.select_related('employer')
        return queryset
```

Notice how this example is using the `is_expanded` utility method as well as `select_related` and `prefetch_related` to efficiently query the database if the field is expanded.

## Expanding a "Many" Relationship <a id="expanding-many"></a>
Set `many` to `True` in the serializer options to make sure "to many" fields are expanded correctly.

```python
class StateSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = State
        fields = ['name', 'population']


class CountrySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Country
        fields = ['name', 'population']

        expandable_fields = {
            'states': (StateSerializer, {'many': True})
        }
```

A request to ```GET /countries?expand=states``` will return:
```python
{
    "id" : 12,
    "name" : "United States",
    "states" : [
      {
        "name" : "Alabama",
        "population": 11000000
      },
      //... more states ... //
      {
        "name" : "Ohio",
        "population": 11000000
      }
    ]
}
```

## Dynamically Setting Fields (Sparse Fields) <a id="dynamically-setting-fields"></a>

You can use either the `fields` or `omit` keywords to declare only the fields you want to include or to specify fields that should be excluded.

Consider this as a default serialized response:
```json
{
  "id" : 13322,
  "name" : "John Doe",
  "country" : {
    "name" : "United States",
    "population": 330000000
  },
  "occupation" : "Programmer",
  "hobbies" : ["rock climbing", "sipping coffee"]
}
```
To whittle down the fields via URL parameters, simply add `?fields=id,name,country` to your requests to get back:
```json
{
  "id" : 13322,
  "name" : "John Doe",
  "country" : {
    "name" : "United States",
    "population: 330000000
  }
}
```
Or, for more specificity, you can use dot-notation,  ```?fields=id,name,country.name```:
```json
{
  "id" : 13322,
  "name" : "John Doe",
  "country" : {
    "name" : "United States",
  }
}
```
Or, if you want to leave out the nested country object, do ```?omit=country```:
```json
{
  "id" : 13322,
  "name" : "John Doe",
  "occupation" : "Programmer",
  "hobbies" : ["rock climbing", "sipping coffee"]
}
```

## Reference serializer as a string (lazy evaluation) <a id="lazy-ref"></a>

To avoid circular import problems, it's possible to lazily evaluate a string reference to you serializer class using this syntax:

```python
expandable_fields = {
    'record_set': ('<app_name>.RelatedSerializer', {'many': True})
}
```

Substitute the name of your Django app where the serializer is found for `<app_name>`.

## Increased re-usability of serializers <a id="increased-reuse"></a>

The `omit` and `fields` options can be passed directly to serializers. Rather than defining a separate, slimmer version of a regular serializer, you can re-use the same serializer and declare which fields you want.

```python
from rest_flex_fields import FlexFieldsModelSerializer

class CountrySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'population', 'capital', 'square_miles']

class PersonSerializer(FlexFieldsModelSerializer):
    country = CountrySerializer(fields=['id', 'name'])

    class Meta:
        model = Person
        fields = ['id', 'name', 'country']


serializer = PersonSerializer(person)
print(serializer.data)

>>>{
  "id": 13322,
  "name": "John Doe",
  "country": {
    "id": 1,
    "name": "United States",
  }
}
```

# Serializer Options

Dynamic field options can be passed in the following ways:
- from the request's query parameters; separate multiple values with a commma
- as keyword arguments directly to the serializer class when its constructed
- from a dictionary placed as the second element in a tuple when defining `expandable_fields`

Approach #1
```
GET /people?expand=friends.hobbies,employer&omit=age
```

Approach #2
```python
serializer = PersonSerializer(
  person, 
  expand=["friends.hobbies", "employer"],
  omit="friends.age"
)
```

Approach #3
```python

class PersonSerializer(FlexFieldsModelSerializer):
  // Your field definitions

  class Meta:
    model = Person
    fields = ["age", "hobbies", "name"]
    expandable_fields = {
      'friends': (
        'serializer.FriendSerializer',
        {'many': True, "expand": ["hobbies"], "omit": "friends.age"}
      )
    }
```

| Option        | Description   |
| ------------- |:-------------:| 
| expand        | Fields to expand; must be configured in the serializer's `expandable_fields` |
| fields        | Fields that should be included; all others will be excluded      | 
| omit          | Fields that should be excluded; all others will be included      | 

# Advanced

## Serializer Introspection

When using an instance of `FlexFieldsModelSerializer`, you can examine the property `expanded_fields` to discover which fields, if any, have been dynamically expanded.

## Use "~all" to Expand All Available Fields <a id="use-all"></a>

You can set ```expand=~all``` to automatically expand all fields that are available for expansion. This will take effect only for the top-level serializer; if you need to also expand fields that are present on deeply nested models, then you will need to explicitly pass their values using dot notation.

## Combining Sparse Fields and Field Expansion  <a id="combining-sparse-and-expanded"></a>

 You may be wondering how things work if you use both the `expand` and `fields` option, and there is overlap. For example, your serialized person model may look like the following by default:

```json
{
  "id": 13322,
  "name": "John Doe",
  "country": {
    "name": "United States",
  }
}
```

However, you make the following request `HTTP GET /person/13322?include=id,name&expand=country`. You will get the following back:

```json
{
  "id": 13322,
  "name": "John Doe"
}
```

The ```include``` field takes precedence over ```expand```. That is, if a field is not among the set that is explicitly alllowed, it cannot be expanded. If such a conflict occurs, you will not pay for the extra database queries - the expanded field will be silently abandoned.

## Query optimization (experimental)

An experimental filter backend is available to help you automatically reduce the number of SQL queries and their transfer size. *This feature has not been tested thorougly and any help testing and reporting bugs is greatly appreciated.* You can add FlexFieldFilterBackend to `DEFAULT_FILTER_BACKENDS` in the settings:
```python
# settings.py

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': (
        'rest_flex_fields.filter_backends.FlexFieldsFilterBackend',
        # ...        
    ),
    # ...
}
```

It will automatically call `select_related` and `prefetch_related` on the current QuerySet by determining which fields are needed from many-to-many and foreign key-related models. For sparse fields requests (`?omit=fieldX,fieldY` or `?fields=fieldX,fieldY`), the backend will automatically call `only(*field_names)` using only the fields needed for serialization. 

**WARNING:** The optimization currently works only for one nesting level.

# Changelog <a id="changelog"></a>

## 0.8.0 (April 2020)
* Adds support for `expand`, `omit` and `fields` query parameters for non-GET requests.
  - The common use case is creating/updating a model instance and returning a serialized response with expanded fields
  - Thanks @kotepillar for raising the issue (#25) and @Crocmagnon for the idea of delaying field modification to `to_representation()`.

## 0.7.5 (February 2020)
* Simplifies declaration of `expandable_fields`
  - If using a tuple, the second element - to define the serializer settings - is now optional.
  - Instead of a tuple, you can now just use the serializer class or a string to lazily reference that class.
  - Updates documentation.

## 0.7.0 (February 2020)
* Adds support for different ways of passing arrays in query strings. Thanks @sentyaev!
* Fixes attribute error when map is supplied to split levels utility function. Thanks @hemache!

## 0.6.1 (September 2019)
* Adds experimental support for automatically SQL query optimization via a `FlexFieldsFilterBackend`. Thanks ADR-007!
* Adds CircleCI config file. Thanks mikeIFTS! 
* Moves declaration of `expandable_fields` to `Meta` class on serialzer for consistency with DRF (will continue to support declaration as class property)
* Python 2 is no longer supported. If you need Python 2 support, you can continue to use older versions of this package.

## 0.5.0 (April 2019)
* Added support for `omit` keyword for field exclusion. Code clean up and improved test coverage.

## 0.3.4 (May 2018)
* Handle case where `request` is `None` when accessing request object from serializer. Thanks @jsatt!

## 0.3.3 (April 2018)
* Exposes `FlexFieldsSerializerMixin` in addition to `FlexFieldsModelSerializer`. Thanks @jsatt!

# Testing

Tests are found in a simplified DRF project in the ```/tests``` folder. Install the project requirements and do ```./manage.py test``` to run them.

# License

See [License](LICENSE.md).
