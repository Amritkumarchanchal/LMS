# tests/models/test_user.py
import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from core.user.models import User, Roles
from core.user.tests.factories import UserFactory

class TestUser(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_user_creation(self):
        """Test basic user creation with factory"""
        assert isinstance(self.user, User)
        assert self.user.email
        assert self.user.role == Roles.STUDENT

    def test_user_roles(self):
        """Test user creation with different roles"""
        for role in Roles.choices:
            user = UserFactory(role=role[0])
            assert user.role == role[0]

    def test_user_str_representation(self):
        """Test string representation of user"""
        expected = f"{self.user.first_name} {self.user.last_name} <{self.user.email}>"
        assert str(self.user) == expected

    def test_user_permissions(self):
        """Test permission checks for different user roles"""
        student = UserFactory(role=Roles.STUDENT)
        admin = UserFactory(role=Roles.ADMIN)
        
        # Test student access
        read, write, delete = student.student_has_access(student)
        assert (read, write, delete) == (True, False, False)
        
        # Test admin access
        read, write, delete = student.admin_has_access(admin)
        assert (read, write, delete) == (True, True, False)