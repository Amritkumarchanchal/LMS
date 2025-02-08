# core/auth/views/login.py:

from drf_spectacular.utils import extend_schema
import requests
from oauth2_provider.models import (
    AccessToken,
    RefreshToken,
    get_application_model,
    Grant,
)
from oauth2_provider.settings import oauth2_settings
from datetime import timedelta
from django.utils.timezone import now
import secrets
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status

from core import settings
from core.auth.constants import DEFAULT_SCOPE
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from core.auth.serializers import LoginSerializer
from core.hardcodes import ae_url


@extend_schema(
    tags=["Auth"],
    summary="Login",
    description="Authenticate the user and generate OAuth1 tokens.",
    request=LoginSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "access_token": {"type": "string"},
                "expires_in": {"type": "integer"},
                "refresh_token": {"type": "string"},
                "token_type": {"type": "string"},
                "scope": {"type": "string"},
            },
        },
        400: {"type": "object", "properties": {"error": {"type": "string"}}},
        401: {"type": "object", "properties": {"error": {"type": "string"}}},
        403: {"type": "object", "properties": {"error": {"type": "string"}}},
    },
)

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]
    client_id = serializer.validated_data["client_id"]
    scope = serializer.validated_data["scope"]

    # Authenticate the user
    user = authenticate(request, email=email, password=password)
    if not user:
        return Response(
            {"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {"error": "User account is inactive."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Validate client application
    Application = get_application_model()
    try:
        application = Application.objects.get(client_id=client_id)
    except Application.DoesNotExist:
        return Response(
            {"error": "Invalid client_id"}, status=status.HTTP_400_BAD_REQUEST
        )
    
    existing_access_token = AccessToken.objects.filter(
        user=user, 
        expires__gt=now(), 
        application=application  # Add application check
    ).order_by('-expires').first()

    # if existing_access_token:

    #     RefreshToken.objects.filter(access_token=existing_access_token).delete()
    #     existing_access_token.delete()

    #     # Optionally notify an external server of the logout
    #     try:
    #         url = f"{ae_url}auth/{user.id}"  # Assuming user ID is part of the DELETE request
    #         response = requests.delete(url)
    #         response.raise_for_status()
    #         print("Successfully logged out on external server.")
    #     except requests.exceptions.RequestException as e:
    #         print(f"Error during logout notification: {e}")

    # Generate an authorization code
    authorization_code = secrets.token_urlsafe(32)
    grant = Grant.objects.create(
        user=user,
        application=application,
        code=authorization_code,
        expires=now() + timedelta(seconds=oauth2_settings.AUTHORIZATION_CODE_EXPIRE_SECONDS),  # type: ignore
        redirect_uri=settings.LOGIN_REDIRECT_URL,
        scope=scope,
    )

    expires = now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)  # type: ignore
    access_token = AccessToken.objects.create(
        user=grant.user,
        application=grant.application,
        token=secrets.token_urlsafe(32),
        expires=expires,
        scope=grant.scope,
    )

    refresh_token = RefreshToken.objects.create(
        user=grant.user,
        token=secrets.token_urlsafe(32),
        access_token=access_token,
        application=grant.application,
    )

    grant.delete()

    payload = {
        "user_id": grant.user.id,
        "access_token": access_token.token,
        "expires_in": oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
    }

    # Make a POST request to the external server with the new access token
    # url = f"{ae_url}auth"
    # try:
    #     response = requests.post(url, json=payload)
    #     response.raise_for_status()
    #     print("Successfully updated login details on external server!")
    # except requests.exceptions.RequestException as e:
    #     print(f"Error during login update: {e}")
    #     raise Exception(f"Error sending login details: {e}")

    return Response(
        {
            "access_token": access_token.token,
            "expires_in": oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
            "refresh_token": refresh_token.token,
            "token_type": "Bearer",
            "scope": access_token.scope,
            "user_id": grant.user.id,
        },
        status=status.HTTP_200_OK,
    )
