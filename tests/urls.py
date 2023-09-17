from django.conf.urls import url, include
from rest_framework import routers
from tests.testapp.views import PetViewSet, TaggedItemViewSet, CountryEventsViewset

# Standard viewsets
router = routers.DefaultRouter()
router.register(r"pets", PetViewSet, basename="pet")
router.register(r"tagged-items", TaggedItemViewSet, basename="tagged-item")
router.register(r"country_events", CountryEventsViewset, basename="country-events")

urlpatterns = [url(r"^", include(router.urls))]
