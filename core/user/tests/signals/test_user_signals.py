# tests/signals/test_user_signals.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from core.user.models import User, Roles
from core.user.signals import validate_institutions, validate_courses
from core.user.tests.factories import UserFactory
from core.course.tests.factories import CourseInstanceFactory
from core.institution.tests.factories import InstitutionFactory

class TestUserSignals(TestCase):
    def setUp(self):
        # Clear any existing signal connections to prevent interference
        m2m_changed.connect(validate_institutions, sender=User.institutions.through)
        m2m_changed.connect(validate_courses, sender=User.courses.through)

    def tearDown(self):
        # Disconnect signals after tests
        m2m_changed.disconnect(validate_institutions, sender=User.institutions.through)
        m2m_changed.disconnect(validate_courses, sender=User.courses.through)

    def test_superadmin_institution_restriction(self):
        """Test that superadmin cannot be assigned to institutions"""
        superadmin = UserFactory(role=Roles.SUPERADMIN)
        institution = InstitutionFactory()
        
        # Using add() directly to trigger the signal
        with self.assertRaises(ValidationError):
            superadmin.institutions.add(institution)

    def test_course_role_restriction(self):
        """Test that only students can be associated with courses"""
        instructor = UserFactory(role=Roles.INSTRUCTOR)
        course = CourseInstanceFactory()
        
        # Using add() directly to trigger the signal
        with self.assertRaises(ValidationError):
            instructor.courses.add(course)