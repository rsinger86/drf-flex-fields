from django.conf import settings


FLEX_FIELDS_OPTIONS = getattr(settings, "REST_FLEX_FIELDS", {})
EXPAND_PARAM = FLEX_FIELDS_OPTIONS.get("EXPAND_PARAM", "expand")
FIELDS_PARAM = FLEX_FIELDS_OPTIONS.get("FIELDS_PARAM", "fields")
OMIT_PARAM = FLEX_FIELDS_OPTIONS.get("OMIT_PARAM", "omit")

if "WILDCARD_EXPAND_VALUES" in FLEX_FIELDS_OPTIONS:
    WILDCARD_VALUES = FLEX_FIELDS_OPTIONS["WILDCARD_EXPAND_VALUES"]
elif "WILDCARD_VALUES" in FLEX_FIELDS_OPTIONS:
    WILDCARD_VALUES = FLEX_FIELDS_OPTIONS["WILDCARD_VALUES"]
else:
    WILDCARD_VALUES = ["~all", "*"]

assert isinstance(EXPAND_PARAM, str), "'EXPAND_PARAM' should be a string"
assert isinstance(FIELDS_PARAM, str), "'FIELDS_PARAM' should be a string"
assert isinstance(OMIT_PARAM, str), "'OMIT_PARAM' should be a string"

if type(WILDCARD_VALUES) not in (list, None):
    raise ValueError("'WILDCARD_EXPAND_VALUES' should be a list of strings or None")


from .utils import *
from .serializers import FlexFieldsModelSerializer
from .views import FlexFieldsModelViewSet
