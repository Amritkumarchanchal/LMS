from django.db import models

from ...auth.permissions import ModelPermissionsMixin
from ...utils.models import TimestampMixin
from . import Course
from ..constants import MODULE_TITLE_MAX_LEN, MODULE_DESCRIPTION_MAX_LEN


# Custom manager for Module model
class ModuleManager(models.Manager):
    """
    Provides custom query methods for the Module model.
    """

    def accessible_by(self, user):
        """
        Returns modules accessible by the given user, based on the user's access to the associated course.

        Args:
            user (User): The user requesting access to modules.

        Returns:
            QuerySet: A queryset of modules accessible to the user.
        """
        # Filter modules whose courses are accessible by the user
        return self.filter(course__in=Course.objects.accessible_by(user))


# Module model
class Module(TimestampMixin, ModelPermissionsMixin, models.Model):
    """
    Represents a module within a course.

    Attributes:
        course (ForeignKey): The course this module belongs to.
        title (str): The title of the module.
        description (str): A detailed description of the module.
        sequence (int): The order of the module within the course.
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=MODULE_TITLE_MAX_LEN)
    description = models.TextField(max_length=MODULE_DESCRIPTION_MAX_LEN)
    sequence = models.PositiveIntegerField(
        help_text="The order of this module in the course."
    )

    # Assign the custom manager
    objects: ModuleManager = ModuleManager()

    class Meta:
        constraints = [
            # Ensure that each module within a course has a unique sequence number
            models.UniqueConstraint(
                fields=["course", "sequence"], name="module_sequence_in_course"
            )
        ]
        ordering = ["sequence"]  # Default ordering by sequence

    def __str__(self):
        """
        Returns a string representation of the module, including its sequence and title.
        """
        return f"Module {self.sequence}: {self.title}"

    def __getattr__(self, name):
        """
        Delegate permission checks to the related course object.

        If a permission-related attribute (e.g., `student_has_access`, `instructor_has_access`)
        is not found on this object, it attempts to fetch it from the related course.

        Args:
            name (str): The name of the attribute being accessed.

        Raises:
            AttributeError: If the attribute does not end with `_has_access` or is not found on the course.

        Returns:
            Callable: The permission-checking method from the related course.
        """
        if name.endswith("_has_access"):
            # Delegate permission checks to the related course
            return getattr(self.course, name)
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )
