# tests/models/test_user_manager.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from core.user.models import User, Roles
import pytest

class TestUserManager(TestCase):
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        assert user.email == 'test@example.com'
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser
        assert user.role == Roles.STUDENT

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='admin123'
        )
        assert admin.is_superuser
        assert admin.is_staff
        assert admin.role == Roles.SUPERADMIN

    def test_create_user_without_email(self):
        """Test creating a user without email raises error"""
        with pytest.raises(ValueError):
            User.objects.create_user(email='', password='test123')