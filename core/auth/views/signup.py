from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework import status
from allauth.account.forms import SignupForm
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from core.auth.serializers import SignupSerializer
from .forms import CustomSignupForm

@extend_schema(
    tags=["Auth"],
    request=SignupSerializer,
    responses={
        201: {"description": "User registered successfully."},
        400: {"description": "Validation error or invalid input data."},
    },
    summary="Signup",
    description="Register a new user in the system.",
)
@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    """
    Register a new user.
    """
    serializer = SignupSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data["email"]
    password = serializer.validated_data["password"]
    first_name = serializer.validated_data["first_name"]
    last_name = serializer.validated_data["last_name"]

    # Construct the data for the SignupForm
    data = {
        "email": email,
        "password1": password,
        "password2": password,
        "first_name": first_name,
        "last_name": last_name,
        "role": serializer.validated_data["role"],
    }

    form = CustomSignupForm(data)
    if form.is_valid():
        user = form.save(request)
        return Response(
            {
                "message": "User registered successfully.",
                "id": user.id,
             }, status=status.HTTP_201_CREATED
        )

    return Response({"errors": form.errors}, status=status.HTTP_400_BAD_REQUEST)