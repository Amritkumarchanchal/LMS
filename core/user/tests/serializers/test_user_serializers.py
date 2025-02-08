# tests/serializers/test_user_serializers.py
from django.test import TestCase
from core.user.serializers import UserSerializer
from core.user.tests.factories import UserFactory
from core.user.models import Roles

class TestUserSerializer(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.serializer = UserSerializer(instance=self.user)

    def test_contains_expected_fields(self):
        """Test serializer contains all expected fields"""
        data = self.serializer.data
        expected_fields = {
            'id', 'email', 'first_name', 'last_name',
            'role', 'is_active', 'institutions', 'courses'
        }
        assert set(data.keys()) >= expected_fields

    def test_validate_user_data(self):
        """Test serializer validation"""
        valid_data = {
            'email': 'test@example.com',
            'password': 'test123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': Roles.STUDENT
        }
        serializer = UserSerializer(data=valid_data)
        assert serializer.is_valid()