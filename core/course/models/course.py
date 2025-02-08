# core/course/models/course.py
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q
from typing import TYPE_CHECKING

from ...auth.permissions import ModelPermissionsMixin
from ...utils.models import TimestampMixin
from ...user.models import Roles  # Only import Roles, not User
from ..constants import COURSE_NAME_MAX_LEN, COURSE_DESCRIPTION_MAX_LEN

if TYPE_CHECKING:
    from ...user.models import User


class VisibilityChoices(models.TextChoices):

    PUBLIC = "public", "Public"  # Publicly visible courses
    PRIVATE = "private", "Private"  # Only visible within certain institutions
    UNLISTED = "unlisted", "Unlisted"  # Hidden courses that require a direct link


class CourseManager(models.Manager):
    def accessible_by(self, user: "User"):
        if user.role in [Roles.SUPERADMIN, Roles.ADMIN]:
            return self.all()

        elif user.role == Roles.MODERATOR:
            return self.filter(
                institution_id__in=user.institutions.values_list("id", flat=True)
            )

        elif user.role == Roles.INSTRUCTOR:
            user_institutions = user.institutions.values_list("id", flat=True)
            return self.filter(
                Q(visibility=VisibilityChoices.PUBLIC)
                | Q(
                    institutions__id__in=user_institutions,
                    visibility=VisibilityChoices.PRIVATE,
                )
                | Q(instructors=user)
            )

        elif user.role == Roles.STAFF:
            user_institutions = user.institutions.values_list("id", flat=True)
            return self.filter(
                Q(visibility=VisibilityChoices.PUBLIC)
                | Q(
                    institutions__id__in=user_institutions,
                    visibility=VisibilityChoices.PRIVATE,
                )
                | Q(id__in=user.personnel_courses.values_list('id', flat=True))
            )

        elif user.role == Roles.STUDENT:
            user_institutions = user.institutions.values_list("id", flat=True)
            return self.filter(
                Q(visibility=VisibilityChoices.PUBLIC)
                | Q(
                    institutions__id__in=user_institutions,
                    visibility=VisibilityChoices.PRIVATE,
                )
                | Q(id__in=user.courses.values_list('id', flat=True))
            )

    def accessible_by_id(self, user: "User", course_id: int):
        """
        Check if a specific course is accessible by the user
        """
        return self.accessible_by(user).filter(id=course_id).first()


class Course(TimestampMixin, ModelPermissionsMixin, models.Model):
    name = models.CharField(max_length=COURSE_NAME_MAX_LEN)
    description = models.TextField(max_length=COURSE_DESCRIPTION_MAX_LEN)
    visibility = models.CharField(
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.PUBLIC,
        help_text="Set the visibility of the course.",
        max_length=21,
    )
    institutions = models.ManyToManyField(
        "institution.Institution", related_name="courses"
    )
    instructors = models.ManyToManyField(
        "user.User", through="CourseInstructor", related_name="instructor_courses"
    )

    objects = CourseManager()

    def __str__(self):
        return self.name

    def student_has_access(self, user: "User"):
        is_read_allowed = (
                user.courses.filter(course=self).exists()  # Enrolled courses

                or self.visibility == VisibilityChoices.PUBLIC
                or (
                        self.visibility == VisibilityChoices.PRIVATE
                        and self.institutions.intersection(user.institutions).exists()
                )

        )
        return (is_read_allowed, False, False)

    def instructor_has_access(self, user: "User"):
        is_course_instructor = self.instructors.filter(pk=user.pk).exists()
        is_read_allowed = (
                is_course_instructor
                or self.visibility == VisibilityChoices.PUBLIC
                or (
                        self.visibility == VisibilityChoices.PRIVATE
                        and self.institutions.intersection(user.institutions).exists()
                )
        )
        return (is_read_allowed, is_course_instructor, False)

    def staff_has_access(self, user: "User"):
        is_course_staff = user.personnel_courses.filter(
            pk=self.pk
        ).exists()
        is_read_allowed = (
                is_course_staff
                or self.visibility == VisibilityChoices.PUBLIC
                or (
                        self.visibility == VisibilityChoices.PRIVATE
                        and self.institutions.intersection(user.institutions).exists()
                )
        )
        return (is_read_allowed, False, False)

    def moderator_has_access(self, user: "User"):
        has_access = self.institutions.intersection(user.institutions).exists()
        return (has_access, has_access, False)

    def admin_has_access(self, user: "User"):
        return (True, True, False)


class CourseInstructor(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    instructor = models.ForeignKey("user.User", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "instructor"], name="unique_course_instructor"
            )
        ]

    def clean(self, *args, **kwargs):
        if self.instructor.role != "instructor":
            raise ValidationError(
                "Only users with the 'instructor' role can be added to the instructors."
            )
        super().clean(*args, **kwargs)

    def __str__(self):
        return f"{self.instructor} - {self.course}"