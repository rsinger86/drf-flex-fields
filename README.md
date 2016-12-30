# Django REST - FlexFields
Flexible, dynamic fields and nested models for Django REST Framework serializers.

# Overview

FlexFields (DRF-FF) for [Django REST Framework](https://django-rest-framework.org) is a package designed to a common baseline of functionality for dynamically setting fields and nested models within DRF serializers. You can dynamically remove unneeded fields, including nested fields, via URL parameters (?fields=name,address.zip) or when configuring serializers. Additionally, you can dynamically expand fields from simple values to complex nested models, or treat fields as "deferred", and expand them on an as-needed basis.

There are similar packages, such as [Dynamic REST](https://github.com/AltSchool/dynamic-rest), which does what this package does and more, but you may not need all those bells and whistles. There is also the more basic [Dynamic Fields Mixin](https://github.com/dbrgn/drf-dynamic-fields), but it lacks functionality for field expansion and dot-notation field customiziation.

This package provides two classes - a viewset class and a serializer class - with minimal magic and entanglement with DRF's foundational classes. 

# Dynamically setting fields

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
            
