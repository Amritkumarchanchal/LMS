from django.db import models
from ..constants import VIDEO_TRANSCRIPT_MAX_LEN
from ...auth.permissions import ModelPermissionsMixin


class Video(ModelPermissionsMixin, models.Model):
    source = models.ForeignKey(
        "Source", on_delete=models.CASCADE, related_name="videos"
    )
    transcript = models.TextField(
        null=True, blank=True, max_length=VIDEO_TRANSCRIPT_MAX_LEN,
        help_text="Transcript of the video."
    )
    start_time = models.PositiveIntegerField(help_text="Start time of the video in seconds.")
    end_time = models.PositiveIntegerField(help_text="End time of the video in seconds.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["source", "start_time", "end_time"], name="unique_video_segment"
            )
        ]
    def admin_has_access(self, user: "User"):
        return True, True, True