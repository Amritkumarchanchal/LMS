# tests/models/test_user_bindings.py
import pytest
from django.test import TestCase
from django.db.utils import IntegrityError
from core.user.models import UserInstitution, UserCourseInstance
from core.user.tests.factories import UserFactory, UserInstitutionFactory
from core.institution.tests.factories import InstitutionFactory

class TestUserBindings(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.institution = InstitutionFactory()

    def test_user_institution_creation(self):
        """Test creating user-institution relationship"""
        user_inst = UserInstitutionFactory(
            user=self.user,
            institution=self.institution
        )
        assert isinstance(user_inst, UserInstitution)
        assert user_inst.user == self.user
        assert user_inst.institution == self.institution

    def test_unique_user_institution_constraint(self):
        """Test unique constraint for user-institution relationship"""
        UserInstitutionFactory(user=self.user, institution=self.institution)
        with pytest.raises(IntegrityError):
            UserInstitutionFactory(user=self.user, institution=self.institution)