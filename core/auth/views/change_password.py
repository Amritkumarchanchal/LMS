from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.serializers import Serializer, CharField
from drf_spectacular.utils import extend_schema

from core.auth.serializers import ChangePasswordSerializer


@extend_schema(
    tags=["Auth"],
    request=ChangePasswordSerializer,
    responses={
        200: {"type": "object", "properties": {"message": {"type": "string"}}},
        400: {"type": "object", "properties": {"error": {"type": "string"}}},
        403: {
            "type": "object",
            "properties": {
                "detail": {
                    "type": "string",
                    "example": "You do not have permission to perform this action.",
                },
            },
        },
    },
    summary="Change Password",
    description="Change the password of an authenticated user.",
)
@permission_classes([IsAuthenticated])
@api_view(["POST"])
def change_password(request):
    """
    Change the user's password.
    """
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user
    old_password = serializer.validated_data["old_password"]
    new_password = serializer.validated_data["new_password"]

    if not user.check_password(old_password):
        return Response(
            {"error": "Old password is incorrect."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.set_password(new_password)
    user.save()
    return Response(
        {"message": "Password changed successfully."}, status=status.HTTP_200_OK
    )
