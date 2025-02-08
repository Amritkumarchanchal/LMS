from rest_framework.response import Response
from rest_framework import status
from oauth2_provider.views import TokenView
from rest_framework.decorators import api_view
from drf_spectacular.utils import extend_schema
from rest_framework.serializers import Serializer, CharField

from core.auth.serializers import RefreshTokenSerializer


@extend_schema(
    tags=["Auth"],
    request=RefreshTokenSerializer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "access_token": {"type": "string"},
                "expires_in": {"type": "integer"},
                "token_type": {"type": "string"},
                "scope": {"type": "string"},
            },
        },
        400: {"type": "object", "properties": {"error": {"type": "string"}}},
    },
    summary="Refresh Token",
    description="Refresh the access token using a valid refresh token.",
)
@api_view(["POST"])
def refresh_token(request):
    serializer = RefreshTokenSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    refresh_token = serializer.validated_data["refresh_token"]
    client_id = serializer.validated_data["client_id"]

    if refresh_token.user != request.user:
        return Response(
            {"error": "Token does not belong to the authenticated user."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token_request_data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }

    token_request = request._request  # Convert DRF request to Django WSGIRequest
    token_request.POST = token_request_data
    token_request.method = "POST"

    token_view = TokenView.as_view()
    response = token_view(token_request)

    return response
