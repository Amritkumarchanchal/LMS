from django.core import serializers
from rest_framework import viewsets
from rest_framework.exceptions import MethodNotAllowed
from drf_spectacular.utils import extend_schema, extend_schema_view
from ..models import Assessment
from ..serializers import AssessmentSerializer
from ...course.models import Section
from django.forms import ValidationError


@extend_schema_view(
    create=extend_schema(
        tags=["Assessment"],
        summary="Create a Assessment",
        description="Create a new Assessment.",
        request=AssessmentSerializer,
        responses=AssessmentSerializer,
    ),
    retrieve=extend_schema(
        tags=["Assessment"],
        summary="Retrieve a Assessment",
        description="Retrieve details of a Assessment by ID.",
        responses=AssessmentSerializer,
    ),
    update=extend_schema(
        tags=["Assessment"],
        summary="Update a Assessment",
        description="Update an existing Assessment by ID.",
        request=AssessmentSerializer,
        responses=AssessmentSerializer,
    ),
    partial_update=extend_schema(
        tags=["Assessment"],
        summary="Partially Update a Assessment",
        description="Partially update fields of a Assessment.",
        request=AssessmentSerializer,
        responses=AssessmentSerializer,
    ),
    destroy=extend_schema(
        tags=["Assessment"],
        summary="Delete a Assessment",
        description="Delete an existing Assessment by ID.",
        responses={"204": "Assessment deleted successfully."},
    ),
)
class AssessmentViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing Assessments.
    """
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer

    def list(self, request, *args, **kwargs):
        """
        Prevent listing of all Assessments.
        """
        raise MethodNotAllowed("GET", detail="Listing is not allowed for this resource.")
    def perform_create(self, serializer):
        """
        Override perform_create to handle section and sequence.
        """
        section_id = self.request.data.get("section")
        sequence = self.request.data.get("sequence")

        if not section_id or not sequence:
            raise ValidationError(
                {"detail": "Both 'section' and 'sequence' are required."}
            )

        # Fetch the Section instance
        section = Section.objects.get(id=section_id)

        # Pass section and sequence to the serializer
        serializer.save(section=section, sequence=sequence)
