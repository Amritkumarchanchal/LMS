# core/assessment/models/assessment.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .. import constants as ct
from ...auth.permissions import ModelPermissionsMixin


class Assessment(ModelPermissionsMixin, models.Model):
    title = models.CharField(max_length=ct.ASSESSMENT_TITLE_MAX_LEN)
    question_visibility_limit = models.IntegerField(
        validators=[
            MinValueValidator(ct.ASSESSMENT_QUESTION_VISIBILITY_LIMIT_MIN_VAL),
            MaxValueValidator(ct.ASSESSMENT_QUESTION_VISIBILITY_LIMIT_MAX_VAL),
        ]
    )
    time_limit = models.IntegerField(
        validators=[
            MinValueValidator(ct.ASSESSMENT_TIME_LIMIT_MIN_VAL),
            MaxValueValidator(ct.ASSESSMENT_TIME_LIMIT_MAX_VAL),
        ],
        help_text="Time limit in seconds",
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Add this field
    updated_at = models.DateTimeField(auto_now=True)  # Add this field


    def __str__(self):
        return self.title
      
    # def admin_has_access(self, user: "User"):
    #     return True, True, True
