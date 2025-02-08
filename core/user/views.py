import requests
from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.course.models import Course
from .models import User, UserInstitution, UserCourseInstance
from .serializers import UserSerializer, UserInstitutionSerializer, UserCoursesSerializer
from core.hardcodes import ae_url


@extend_schema_view(
    list=extend_schema(
        tags=["Users"],
        summary="List Users",
        description="Retrieve a list of all users.",
        responses=UserSerializer,
    ),
    create=extend_schema(
        tags=["Users"],
        summary="Create User",
        description="Create a new user with the provided data.",
        request=UserSerializer,
        responses=UserSerializer,
    ),
    retrieve=extend_schema(
        tags=["Users"],
        summary="Retrieve User",
        description="Get detailed information for a specific user.",
        responses=UserSerializer,
    ),
    update=extend_schema(
        tags=["Users"],
        summary="Update User",
        description="Update all fields of an existing user.",
        request=UserSerializer,
        responses=UserSerializer,
    ),
    partial_update=extend_schema(
        tags=["Users"],
        summary="Partially Update User",
        description="Update selected fields of an existing user.",
        request=UserSerializer,
        responses=UserSerializer,
    ),
    destroy=extend_schema(
        tags=["Users"],
        summary="Delete User",
        description="Delete an existing user.",
        responses={"204": "User deleted successfully."},
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["User Institutions"],
        summary="List User Institution Associations",
        description="Retrieve a list of all user-institution associations.",
        responses=UserInstitutionSerializer,
    ),
    create=extend_schema(
        tags=["User Institutions"],
        summary="Create User Institution Association",
        description="Create a new association between a user and an institution.",
        request=UserInstitutionSerializer,
        responses=UserInstitutionSerializer,
    ),
    retrieve=extend_schema(
        tags=["User Institutions"],
        summary="Retrieve User Institution Association",
        description="Get details for a specific user-institution association.",
        responses=UserInstitutionSerializer,
    ),
    update=extend_schema(
        tags=["User Institutions"],
        summary="Update User Institution Association",
        description="Update all fields of an existing user-institution association.",
        request=UserInstitutionSerializer,
        responses=UserInstitutionSerializer,
    ),
    partial_update=extend_schema(
        tags=["User Institutions"],
        summary="Partially Update User Institution Association",
        description="Update selected fields of an existing user-institution association.",
        request=UserInstitutionSerializer,
        responses=UserInstitutionSerializer,
    ),
    destroy=extend_schema(
        tags=["User Institutions"],
        summary="Delete User Institution Association",
        description="Delete an existing user-institution association.",
        responses={"204": "Association deleted successfully."},
    ),
)
class UserInstitutionViewSet(viewsets.ModelViewSet):
    queryset = UserInstitution.objects.all()
    serializer_class = UserInstitutionSerializer


@extend_schema_view(
    list=extend_schema(
        tags=["User Courses"],
        summary="List User Course Instances",
        description="Retrieve a list of all user course instances.",
        responses=UserCoursesSerializer,
    ),
    create=extend_schema(
        tags=["User Courses"],
        summary="Create User Course Instance",
        description="Create a new course instance for a user.",
        request=UserCoursesSerializer,
        responses=UserCoursesSerializer,
    ),
    retrieve=extend_schema(
        tags=["User Courses"],
        summary="Retrieve User Course Instance",
        description="Get details for a specific user course instance.",
        responses=UserCoursesSerializer,
    ),
    update=extend_schema(
        tags=["User Courses"],
        summary="Update User Course Instance",
        description="Update all fields of an existing user course instance.",
        request=UserCoursesSerializer,
        responses=UserCoursesSerializer,
    ),
    partial_update=extend_schema(
        tags=["User Courses"],
        summary="Partially Update User Course Instance",
        description="Update selected fields of an existing user course instance.",
        request=UserCoursesSerializer,
        responses=UserCoursesSerializer,
    ),
    destroy=extend_schema(
        tags=["User Courses"],
        summary="Delete User Course Instance",
        description="Delete an existing user course instance.",
        responses={"204": "Course instance deleted successfully."},
    ),
)
class UserCoursesViewSet(viewsets.ModelViewSet):
    queryset = UserCourseInstance.objects.all()
    serializer_class = UserCoursesSerializer

    def perform_create(self, serializer):
        # Save the course-user relationship
        instance = serializer.save()

        # Fetch course details for the payload
        course = instance.course
        course = Course.objects.get(id=course.id)

        modules = course.modules.all()

        # Construct `modules` part of the payload
        modules_payload = []
        for module in modules:
            sections_payload = []
            for section in module.sections.all():
                items_payload = []
                for item in section.section_item_info.all():
                    items_payload.append({
                        "sectionItemId": item.prefixed_item_id,
                        "sequence": item.sequence,
                    })
                sections_payload.append({
                    "sectionId": f"{section.id}",
                    "sequence": section.sequence,
                    "sectionItems": items_payload,
                })
            modules_payload.append({
                "moduleId": f"{module.id}",
                "sequence": module.sequence,
                "sections": sections_payload,
            })

        # Prepare the full payload
        payload = {
            "courseInstanceId": str(course.id),
            "studentIds": [str(instance.user.id)],
            "modules": modules_payload,
        }

        # Send the POST request
        url = f"{ae_url}v1/course-progress/initialize-progress"

        try:
            response = requests.post(url, json=payload)
            print("Successfully sent!")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # Handle request exceptions if needed
            raise Exception(f"Error sending course initialization: {e}")