from django.db import models

from ...auth.permissions import ModelPermissionsMixin
from ...utils.models import TimestampMixin
from . import Module
from .. import constants as ct


# Custom manager for Section model
class SectionManager(models.Manager):
    """
    Provides custom query methods for the Section model.
    """

    def accessible_by(self, user):
        """
        Returns sections accessible by the given user, based on the user's access to the associated module.

        Args:
            user (User): The user requesting access to sections.

        Returns:
            QuerySet: A queryset of sections accessible by the user.
        """
        # Filter sections whose modules are accessible by the user
        return self.filter(module__in=Module.objects.accessible_by(user))


# Section model
class Section(TimestampMixin, ModelPermissionsMixin, models.Model):
    """
    Represents a section within a module.

    Attributes:
        module (ForeignKey): The module this section belongs to.
        title (str): The title of the section.
        description (str): A detailed description of the section.
        sequence (int): The order of the section within the module.
    """

    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name="sections"
    )
    title = models.CharField(max_length=ct.SECTION_TITLE_MAX_LEN)
    description = models.TextField(max_length=ct.SECTION_DESCRIPTION_MAX_LEN)
    sequence = models.PositiveIntegerField(
        help_text="The order of this section within the module."
    )

    # Assign the custom manager
    objects: SectionManager = SectionManager()

    class Meta:
        constraints = [
            # Ensure that each section within a module has a unique sequence number
            models.UniqueConstraint(
                fields=["module", "sequence"], name="section_sequence_in_module"
            )
        ]
        ordering = ["sequence"]  # Default ordering by sequence

    def __str__(self):
        """
        Returns a string representation of the section, including its sequence and module.
        """
        return f"Section {self.sequence}: {self.title} (Module {self.module.sequence})"

    def __getattr__(self, name):
        """
        Delegate permission checks to the related module object.

        If a permission-related attribute (e.g., `student_has_access`, `instructor_has_access`) is not
        found on this object, it attempts to fetch it from the related module.

        Args:
            name (str): The name of the attribute being accessed.

        Raises:
            AttributeError: If the attribute does not end with `_has_access` or is not found on the module.

        Returns:
            Callable: The permission-checking method from the related module.
        """
        if name.endswith("_has_access"):
            # Delegate permission checks to the related module
            return getattr(self.module, name)
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

