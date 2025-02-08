from django.db import models, transaction
from . import Section

class SectionItemType(models.TextChoices):
    ARTICLE = "article", "Article"
    ASSESSMENT = "assessment", "Assessment"
    VIDEO = "video", "Video"


class SectionItemInfo(models.Model):
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="section_item_info",
        help_text="The section this item belongs to.",
    )
    sequence = models.PositiveIntegerField(
        help_text="The order of this item within the section."
    )
    item_type = models.CharField(
        choices=SectionItemType.choices,
        max_length=20,
        help_text="The type of this section item (video, article, etc.).",
    )
    item_id = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["section", "sequence"],
                name="unique_section_sequence",
            )
        ]

    def __str__(self):
        return f"{self.section} - Item Sequence {self.sequence}"

    @property
    def prefixed_item_id(self):
        prefix_map = {
            SectionItemType.VIDEO: "v",
            SectionItemType.ASSESSMENT: "a",
            SectionItemType.ARTICLE: "ar",
        }
        prefix = prefix_map.get(self.item_type, "")
        return f"{prefix}{self.item_id}"

    @staticmethod
    def create_item(section, sequence, item_type, item_instance):
        """
        Creates a record in SectionItemInfo in a transaction-safe way.
        """
        with transaction.atomic():
            return SectionItemInfo.objects.create(
                section=section,
                sequence=sequence,
                item_type=item_type,
                item_id=item_instance.id,
            )
