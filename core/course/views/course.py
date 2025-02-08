# core/course/views/course.py

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..serializers import CourseListSerializer, CourseDetailSerializer
from ..models import Course
from ...utils.helpers import get_user


from rest_framework import viewsets
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from ..serializers import CourseListSerializer, CourseDetailSerializer
from ..models import Course
from ...utils.helpers import get_user


@extend_schema_view(
    list=extend_schema(
        tags=["Course"],
        summary="List Courses",
        description="Retrieve a list of courses accessible by the current user.",
        responses=CourseListSerializer,
    ),
    retrieve=extend_schema(
        tags=["Course"],
        summary="Retrieve a Course",
        description="Retrieve detailed information for a single course.",
        responses=CourseDetailSerializer,
    ),
    create=extend_schema(
        tags=["Course"],
        summary="Create a Course",
        description="Create a new course with the provided data.",
        request=CourseDetailSerializer,
        responses=CourseDetailSerializer,
    ),
    update=extend_schema(
        tags=["Course"],
        summary="Update a Course",
        description="Update an existing course with new data.",
        request=CourseDetailSerializer,
        responses=CourseDetailSerializer,
    ),
    partial_update=extend_schema(
        tags=["Course"],
        summary="Partially Update a Course",
        description="Update selected fields of an existing course.",
        request=CourseDetailSerializer,
        responses=CourseDetailSerializer,
    ),
    destroy=extend_schema(
        tags=["Course"],
        summary="Delete a Course",
        description="Delete an existing course.",
        responses={"204": "Course deleted successfully."},
    ),
)
class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == 'retrieve':
            # For single course retrieval, use the new method
            course = Course.objects.accessible_by_id(
                get_user(self.request.user), 
                self.kwargs.get('pk')
            )
            return Course.objects.filter(id=course.id) if course else Course.objects.none()
        
        # For list and other actions, use the existing method
        return Course.objects.accessible_by(get_user(self.request.user))

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CourseDetailSerializer if self.action == "retrieve" else CourseListSerializer
        return CourseDetailSerializer