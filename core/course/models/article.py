from django.db import models
from ..constants import ARTICLE_MAX_LENGTH
from ...auth.permissions import ModelPermissionsMixin


class Article(ModelPermissionsMixin, models.Model):
    content = models.TextField(max_length=ARTICLE_MAX_LENGTH)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def admin_has_access(self, user: "User"):
        return True, True, True
