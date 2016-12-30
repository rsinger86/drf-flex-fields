# Django REST - FlexFields
Flexible, dynamic fields and nested models for Django REST Framework serializers.

# Overview

FlexFields (DRF-FF) for [Django REST Framework](https://django-rest-framework.org) is a package designed to provide a common baseline of functionality for dynamically setting fields and nested models within DRF serializers. You can dynamically remove unneeded fields, including nested fields, via URL parameters (?fields=name,address.zip) or when configuring serializers. Additionally, you can dynamically expand fields from simple values to complex nested models, or treat fields as "deferred", and expand them on an as-needed basis.

This package is designed for simplicity and provides two classes - a viewset class and a serializer class - with minimal magic and entanglement with DRF's foundational classes. If you are familar with Django REST Framework, it shouldn't take you long to read over the code and see how it works. 

There are similar packages, such as the powerful [Dynamic REST](https://github.com/AltSchool/dynamic-rest), which does what this package does and more, but you may not need all those bells and whistles. There is also the more basic [Dynamic Fields Mixin](https://github.com/dbrgn/drf-dynamic-fields), but it lacks functionality for field expansion and dot-notation field customiziation.

# Setup 

To use this package's functionality your viewsets need to subclass ```FlexFieldsModelViewSet``` and your serializers need to subclass ```FlexFieldsModelSerializer```:

```
from rest_flex_fields import FlexFieldsModelViewSet, FlexFieldsModelViewSet

class PersonViewSet(FlexFieldsModelSerializer):
  queryset = models.Person.objects.all()
  serializer_class = PersonSerializer	
  
class PersonSerializer(FlexFieldsModelSerializer):
  class Meta:
    model = Person
    fields = ('id', 'name', 'country', 'occupation')
```
# Dynamic field expansion

To define an expandable field, add it to the ```expandable_fields``` within your serializer:
```
class CountrySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Company  
        fields = ['name', 'population']


class PersonSerializer(FlexFieldsModelSerializer):
    country = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Person  
        fields = ['id', 'name', 'country', 'occupation']

    expandable_fields = {
        'country': (CountrySerializer, {'source': 'country', 'fields': ['name']})
    }
```

If the default serialized response is the following:
```
{
  "id" : 13322
  "name" : "John Doe",
  "country" : 12,
  "occupation" : "Programmer",
}
```
When you do a ```GET /person/13322?expand=country```, the response will change to:

```
{
  "id" : 13322
  "name" : "John Doe",
  "country" : {
    "name" : "United States"
  },
  "occupation" : "Programmer",
}
```
Notice how ```population``` was ommitted from the nested ```country``` object. This is because ```fields``` was set to ```['name']```. You will learn more about this later on. 

## Deferred Fields
Alternatively, you could treat ```country``` as a so-called "deferred" field by not defining it among the default fields (where in this example, it is by default the related PK). 

## Deep, Nested Expansion
Let's say you add a nested model serializer to the country serializer above:

```
class StateSerializer(FlexFieldsModelSerializer):
    class Meta:
        model = State  
        fields = ['name', 'population']
        
        
class CountrySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Company  
        fields = ['name', 'population']

    expandable_fields = {
        'states': (StateSerializer, {'source': 'country', 'many': True})
    }
    
class PersonSerializer(FlexFieldsModelSerializer):
    country = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Person  
        fields = ['id', 'name', 'country', 'occupation']

    expandable_fields = {
        'country': (CountrySerializer, {'source': 'country', 'fields': ['name']})
    }
```

Your default serialized response might be the following for ```person``` and ```country```, respectively:
```
{
  "id" : 13322
  "name" : "John Doe",
  "country" : 12,
  "occupation" : "Programmer",
}

{
  "id" : 12
  "name" : "United States",
  "states" : "http://www.api.com/countries/12/states"
}
```
But if you do a ```GET /person/13322?expand=country.states```, it will be:
```
{
  "id" : 13322
  "name" : "John Doe",
  "occupation" : "Programmer",
  "country" : {
    "id" : 12
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

## Configuration from Serializer Options

You could accomplish the same result (expanding the ```states``` field within the embedded country serializer) by explicitly passing the ```expand``` option within your serializer:

```
class PersonSerializer(FlexFieldsModelSerializer):
    
    class Meta:
        model = Person  
        fields = ['id', 'name', 'country', 'occupation']

    expandable_fields = {
        'country': (CountrySerializer, {'source': 'country', 'expand': ['states']})
    }
```


# Dynamically Setting Fields

## From URL Parameters
You can dynamically set fields, with the configuration originating from the URL parameters or serializer options. 

Consider this as a default serialized response:
```
{
  "id" : 13322
  "name" : "John Doe",
  "country" : {
    "name" : "United States",
    "population: 330000000
  },
  "occupation" : "Programmer",
  "hobbies" : ["rock climbing", "sipping coffee"}
}
```
To whittle down the fields via URL parameters, simply add ```?fields=id,name,country``` to your requests to get back:
```
{
  "id" : 13322
  "name" : "John Doe",
  "country" : {
    "name" : "United States",
    "population: 330000000
  }
}
```
Or, for more specificity, you can use dot-notation,  ```?fields=id,name,country.name```:
```
{
  "id" : 13322
  "name" : "John Doe",
  "country" : {
    "name" : "United States",
  }
}
```
## From Serializer Options
You could accomplish the same outcome as the example above by passing options to your serializers. With this approach, you lose runtime dynamicism, but gain the ability to re-use serializers, rather than creating a simplified copy of a serializer for the purposes of embedding it. 
```
from rest_flex_fields import FlexFieldsModelSerializer

class CountrySerializer(FlexFieldsModelSerializer):
    class Meta:
        model = Country  
        fields = ['id', 'name', 'population']
        
class PersonSerializer(FlexFieldsModelSerializer):
    country: CountrySerializer(fields=['name'])
    class Meta:
        model = Person  
        fields = ['id', 'name', 'country', 'occupation', 'hobbies']


serializer = PersonSerializer(person, fields=["id", "name", "country.name"])
print(serializer.data)
>>> {
  "id" : 13322
  "name" : "John Doe",
  "country" : {
    "name" : "United States",
  }
}

 ```
 
 # Combining Dynamically-Set Fields and Field Expansion
 You may be wondering how things work if you use both the ```expand``` and ```fields``` option, and there is overlap. For example, your serialized person model may look like the following by default:
```
{
  "id" : 13322
  "name" : "John Doe",
  "country" : {
    "name" : "United States",
  }
}
```
However, you make the following request ```HTTP GET /person/13322?include=id,name&expand=country```. You will get the following back:
```
{
  "id" : 13322
  "name" : "John Doe"
}
```
The ```include``` field takes precedence over ```expand```. That is, if a field is not among the set that is explicitly alllowed, it cannot be expanded. If such a conflict occurs, you will not pay for the extra database queries - the expanded field will be silently abandoned.  

