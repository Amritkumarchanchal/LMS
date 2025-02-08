from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserInstitutionViewSet, UserCoursesViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'user-institutions', UserInstitutionViewSet)
router.register(r'user-course', UserCoursesViewSet)

# urlpatterns = router.urls

urlpatterns = [
    path('api/', include(router.urls)),
]
