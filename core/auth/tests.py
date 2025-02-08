from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from oauth2_provider.models import Application, AccessToken, RefreshToken
from django.utils.timezone import now
from datetime import timedelta
import pytest
from unittest.mock import Mock
from django.contrib.auth.models import AnonymousUser

from core.user.models import User, Roles
from core.auth.permissions import RoleBasedPermission, AllowAllAuthenticatedUsers
from core.auth.serializers import (
    LoginSerializer, SignupSerializer, LogoutSerializer,
    ChangePasswordSerializer, PasswordResetSerializer
)

# Test Factories
class UserFactory:
    @staticmethod
    def create(
        email=None,
        password="testpass123",
        first_name="Test",
        last_name="User",
        role=Roles.STUDENT,
        is_active=True
    ):
        if email is None:
            # Generate unique email
            import uuid
            email = f"test_{uuid.uuid4().hex[:10]}@example.com"
            
        return User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_active=is_active
        )

class ApplicationFactory:
    @staticmethod
    def create(user, name="Test App"):
        return Application.objects.create(
            name=name,
            user=user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )

# Serializer Tests
class TestLoginSerializer(TestCase):
    def test_valid_data(self):
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'client_id': 'test_client_id'
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
    def test_invalid_email(self):
        data = {
            'email': 'invalid-email',
            'password': 'testpass123',
            'client_id': 'test_client_id'
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

class TestSignupSerializer(TestCase):
    def test_valid_data(self):
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': Roles.STUDENT
        }
        serializer = SignupSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_missing_required_fields(self):
        data = {'email': 'test@example.com'}
        serializer = SignupSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password', serializer.errors)
        self.assertIn('first_name', serializer.errors)
        self.assertIn('last_name', serializer.errors)
        self.assertIn('role', serializer.errors)

# View Tests
class TestSignupView(APITestCase):
    def setUp(self):
        self.url = reverse('signup')
        self.valid_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'role': Roles.STUDENT
        }

    def test_successful_signup(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.valid_data['email']).exists())

    def test_duplicate_email(self):
        # Create user first
        User.objects.create_user(email=self.valid_data['email'], password='test123')
        # Try to create another user with same email
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TestLoginView(APITestCase):
    def setUp(self):
        self.url = reverse('login')
        self.user = UserFactory.create()
        self.application = ApplicationFactory.create(self.user)
        self.valid_data = {
            'email': self.user.email,  # Use the actual user's email
            'password': 'testpass123',
            'client_id': self.application.client_id,
            'scope': 'read write'
        }

    def test_successful_login(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_invalid_credentials(self):
        self.valid_data['password'] = 'wrongpass'
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  # Changed to 401

from rest_framework_simplejwt.tokens import RefreshToken as SimpleJWTRefreshToken

class TestLogoutView(APITestCase):
    def setUp(self):
        self.url = reverse('logout_custom')
        self.user = UserFactory.create()
        self.application = ApplicationFactory.create(self.user)
        
        # Create access token
        self.access_token = AccessToken.objects.create(
            user=self.user,
            token='test_token',
            application=self.application,
            expires=now() + timedelta(days=1),
            scope='read write'
        )
        
        # Create refresh token
        self.refresh_token = RefreshToken.objects.create(
            user=self.user,
            token='test_refresh',
            application=self.application,
            access_token=self.access_token
        )
        
        # Get JWT token for authentication
        self.jwt_token = SimpleJWTRefreshToken.for_user(self.user).access_token

    def test_successful_logout(self):
        # Authenticate with JWT token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        
        # Send the OAuth2 token in the request body
        response = self.client.post(self.url, {'token': self.access_token.token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(AccessToken.objects.filter(token=self.access_token.token).exists())

    def test_invalid_token(self):
        # Authenticate with JWT token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        
        # Send invalid token in request body
        response = self.client.post(self.url, {'token': 'invalid_token'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class TestChangePasswordView(APITestCase):
    def setUp(self):
        self.url = reverse('change_password')
        self.user = UserFactory.create()
        
        # Get JWT token for authentication
        self.jwt_token = SimpleJWTRefreshToken.for_user(self.user).access_token
        
        # Set up the authorization header with JWT token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.jwt_token}')
        
        self.valid_data = {
            'old_password': 'testpass123',
            'new_password': 'newtestpass123'
        }

    def test_successful_password_change(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.valid_data['new_password']))

    def test_incorrect_old_password(self):
        self.valid_data['old_password'] = 'wrongpass'
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated(self):
        # Remove authentication
        self.client.credentials()
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# Permission Tests
class TestRoleBasedPermission(TestCase):
    def setUp(self):
        self.permission = RoleBasedPermission()
        self.factory = APIRequestFactory()

    def test_has_permission(self):
        roles_to_test = [Roles.STUDENT, Roles.INSTRUCTOR, Roles.ADMIN]
        
        for role in roles_to_test:
            user = UserFactory.create(role=role)
            request = self.factory.get('/')
            request.user = user
            result = self.permission.has_permission(request, None)
            
            if role == Roles.STUDENT:
                self.assertTrue(result)  # Students can read
            else:
                self.assertTrue(result)  # Others have full access

class TestAllowAllAuthenticatedUsers(TestCase):
    def setUp(self):
        self.permission = AllowAllAuthenticatedUsers()
        self.factory = APIRequestFactory()

    def test_authenticated_user(self):
        user = UserFactory.create()
        request = self.factory.get('/')
        request.user = user
        self.assertTrue(self.permission.has_permission(request, None))

    def test_unauthenticated_user(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        self.assertFalse(self.permission.has_permission(request, None))