# tests/views/test_user_views.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from core.user.models import User, Roles
from core.user.tests.factories import UserFactory

class TestUserViewSet(APITestCase):
    def setUp(self):
        self.admin_user = UserFactory(role=Roles.ADMIN)
        self.client.force_authenticate(user=self.admin_user)
        self.list_url = reverse('user-list')  # Use reverse to get the correct URL

    def test_list_users(self):
        """Test retrieving user list"""
        UserFactory.create_batch(3)  # Create some test users
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 3  # Should include the admin user too

    def test_create_user(self):
        """Test creating new user"""
        data = {
            'email': 'new@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': Roles.STUDENT.value
        }
        response = self.client.post(self.list_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='new@example.com').exists()