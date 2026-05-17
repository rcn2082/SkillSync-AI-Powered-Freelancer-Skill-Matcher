from rest_framework.routers import DefaultRouter
from .views import FreelancerViewSet, ClientViewSet

router = DefaultRouter()
router.register(r"freelancers", FreelancerViewSet, basename="freelancers")
router.register(r"clients", ClientViewSet, basename="clients")

urlpatterns = router.urls
