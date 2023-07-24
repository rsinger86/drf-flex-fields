from django.urls import include, path
from rest_framework import routers
from tests.testapp.views import PetViewSet, TaggedItemViewSet

# Standard viewsets
router = routers.DefaultRouter()
router.register(r"pets", PetViewSet, basename="pet")
router.register(r"tagged-items", TaggedItemViewSet, basename="tagged-item")

urlpatterns = [path("", include(router.urls))]
