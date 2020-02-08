from django.conf.urls import url, include
from rest_framework import routers
from tests.testapp.views import PetViewSet


# Standard viewsets
router = routers.DefaultRouter()
router.register(r"pets", PetViewSet, basename="pet")

urlpatterns = [url(r"^", include(router.urls))]
