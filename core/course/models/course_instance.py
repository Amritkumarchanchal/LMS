from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q

from ...auth.permissions import ModelPermissionsMixin
from ...utils.models import TimestampMixin
from . import VisibilityChoices
from ...user.models import Roles, User


# Custom manager for CourseInstance model
class CourseInstanceManager(models.Manager):
    """
    Provides custom query methods for the CourseInstance model.
    """

    def accessible_by(self, user: User):
        """
        Returns course instances accessible by the given user, depending on their role.

        Args:
            user (User): The user requesting access to course instances.

        Returns:
            QuerySet: A queryset of course instances accessible to the user.
        """
        if user.role in [Roles.SUPERADMIN, Roles.ADMIN]:
            # Superadmins and admins have access to all course instances
            return self.all()

        elif user.role == Roles.MODERATOR:
            # Moderators can access course instances linked to their institutions
            return self.filter(
                course_institutions_id__in=user.institutions.values_list("id", flat=True)
            )

        elif user.role == Roles.INSTRUCTOR:
            # Instructors can access:
            # - Public courses
            # - Private courses in their institutions
            # - Courses where they are explicitly listed as instructors
            user_institutions = user.institutions.values_list("id", flat=True)
            return self.filter(
                Q(course_visibility=VisibilityChoices.PUBLIC)
                | Q(
                    course_institutions__id__in=user_institutions,
                    course_visibility=VisibilityChoices.PRIVATE,
                )
                | Q(course_instructors__contains=user)
            )

        elif user.role == Roles.STAFF:
            # Staff members can access:
            # - Public courses
            # - Private courses in their institutions
            # - Courses they are assigned to as personnel
            user_institutions = user.institutions.values_list("id", flat=True)
            return self.filter(
                Q(course_visibility=VisibilityChoices.PUBLIC)
                | Q(
                    course_institutions__id__in=user_institutions,
                    course_visibility=VisibilityChoices.PRIVATE,
                )
                | Q(personnel=user)
            )

        elif user.role == Roles.STUDENT:
            # Students can only access courses they are enrolled in
            return user.courses.all()


# CourseInstance model
class CourseInstance(TimestampMixin, ModelPermissionsMixin, models.Model):
    """
    Represents a specific instance of a course, with start and end dates.

    Attributes:
        course (ForeignKey): The course this instance is related to.
        start_date (Date): The start date of the course instance.
        end_date (Date): The end date of the course instance.
        personnel (ManyToMany): Users assigned to this course instance as personnel.
    """

    course = models.ForeignKey(
        "Course", on_delete=models.CASCADE, related_name="instances"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    personnel = models.ManyToManyField(
        "user.User", through="CoursePersonnel", related_name="personnel_courses"
    )

    # Assign the custom manager
    objects: CourseInstanceManager = CourseInstanceManager()

    class Meta:
        constraints = [
            # Ensure unique course instances for the same course with the same start and end dates
            models.UniqueConstraint(
                fields=["course", "start_date", "end_date"],
                name="unique_course_instance",
            )
        ]

    def __str__(self):
        """
        Returns a string representation of the course instance, including the course and its start and end dates.
        """
        return f"{self.course} - {self.start_date} to {self.end_date}"

    def __getattr__(self, name):
        """
        Dynamically delegate access methods to the related Course instance,
        except for staff-specific access logic.

        Args:
            name (str): The name of the attribute being accessed.

        Raises:
            AttributeError: If the attribute is not found.

        Returns:
            Callable: The permission-checking method from the related course.
        """
        if name in {
            "student_has_access",
            "instructor_has_access",
            "moderator_has_access",
            "admin_has_access",
            "superadmin_has_access",
        }:
            return getattr(self.course, name)
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    # def has_write_permission(self, user):
    #     """Check if user has write permission for this course instance"""
    #     if user.role in [Roles.SUPERADMIN, Roles.ADMIN]:
    #         return True
    #     # elif user.role == Roles.MODERATOR:
    #     #     return user.institutions.filter(
    #     #         id__in=self.course.course_institutions.values_list("id", flat=True)).exists()
    #     return False

    def staff_has_access(self, user: User):
        """
        Determines if a staff member has access to this course instance.

        Args:
            user (User): The user requesting access.

        Returns:
            Tuple: A tuple of booleans indicating read, write, and delete permissions.
        """
        course_access = self.course.staff_has_access(user)
        is_instance_personnel = self.personnel.filter(pk=user.pk).exists()
        return (course_access[0], is_instance_personnel, course_access[2])


# Allowed roles for personnel
class PersonnelAllowedRoles(models.TextChoices):
    MODERATOR = "moderator", "Moderator"
    STAFF = "staff", "Staff"
    ADMIN = "admin", "Admin"

    @classmethod
    def choices_to_string(cls):
        """
        Returns a comma-separated string of allowed role names.
        """
        return ", ".join([choice[1] for choice in cls.choices])


# Through table for personnel-course relationships
class CoursePersonnel(models.Model):
    """
    Represents the relationship between a course instance and its personnel.

    Attributes:
        course (ForeignKey): The course instance the personnel is assigned to.
        personnel (ForeignKey): The personnel assigned to the course instance.
    """

    course = models.ForeignKey(CourseInstance, on_delete=models.CASCADE)
    personnel = models.ForeignKey("user.User", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            # Ensure unique personnel assignments for each course instance
            models.UniqueConstraint(
                fields=["course", "personnel"], name="unique_course_personnel"
            )
        ]

    def save(self, *args, **kwargs):
        """
        Validates the personnel's role before saving.

        Raises:
            ValidationError: If the personnel's role is not in the allowed roles.
        """
        if self.personnel.role not in PersonnelAllowedRoles.values:
            raise ValidationError(
                f"Only users with one of {PersonnelAllowedRoles.choices_to_string()} roles can be added as personnel."
            )
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Returns a string representation of the personnel assignment.
        """
        return f"{self.personnel} - {self.course}"
