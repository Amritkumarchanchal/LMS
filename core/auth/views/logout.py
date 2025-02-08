# core/auth/views/logout.py:

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from oauth2_provider.models import AccessToken, RefreshToken
from rest_framework.decorators import api_view, permission_classes
import requests

from core.auth.permissions import AllowAllAuthenticatedUsers
from core.auth.serializers import LogoutSerializer
from core.user.models import Roles, User
from core.hardcodes import ae_url


@extend_schema(
    tags=["Auth"],
    request=LogoutSerializer,
    responses={
        200: {"type": "object", "properties": {"message": {"type": "string"}}},
        400: {"type": "object", "properties": {"error": {"type": "string"}}},
    },
    summary="Logout",
    description="Revoke the user's access token and logout the user.",
)
@api_view(["POST"])
@permission_classes([AllowAllAuthenticatedUsers])
def logout(request):
    """
    Revoke the user's access token.
    """
    serializer = LogoutSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    token = serializer.validated_data.get("token")
    user: User = request.user
    print("LALLALALALALAALL")

    try:
        # Fetch the AccessToken object
        access_token = AccessToken.objects.get(token=token)

        # Ensure the token belongs to the authenticated user
        if access_token.user != request.user:
            # SuperAdmins and Admins can logout students.
            if access_token.user.role == Roles.STUDENT and user.role in [Roles.SUPERADMIN, Roles.ADMIN, Roles.MODERATOR]:
                RefreshToken.objects.filter(access_token=access_token).delete()
                access_token.delete()

                # try:
                #     url = f"{ae_url}auth/{access_token.user.id}"
                #     response = requests.delete(url)
                #     response.raise_for_status()
                #     print("Successfully logged out on external server.")
                # except requests.exceptions.RequestException as e:
                #     print(f"Error in DELETE request: {e}")


                return Response(
                    {"message": "Student Logged out successfully."}, status=status.HTTP_200_OK
                )

            return Response(
                {"error": "Token does not belong to the authenticated user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Delete the RefreshToken and AccessToken
        print("YAHAN ERROR HAI")
        RefreshToken.objects.filter(access_token=access_token).delete()
        access_token.delete()

        # try:
        #     url = f"{ae_url}auth/{user.id}"
        #     response = requests.delete(url)
        #     response.raise_for_status()
        #     print("Successfully logged out on external server.")
        # except requests.exceptions.RequestException as e:
        #     print(f"Error in DELETE request: {e}")

        return Response(
            {"message": "Logged out successfully."}, status=status.HTTP_200_OK
        )

    except AccessToken.DoesNotExist:
        return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)