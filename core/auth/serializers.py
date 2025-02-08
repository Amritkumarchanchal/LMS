from rest_framework.serializers import Serializer, EmailField, CharField
from core.auth.constants import DEFAULT_SCOPE


class LoginSerializer(Serializer):
    email = EmailField(
        help_text="The email address of the user attempting to login.",
        required=True
    )
    password = CharField(
        help_text="The password associated with the user's account.",
        required=True
    )
    client_id = CharField(
        help_text="The client ID associated with the OAuth2 application.",
        required=True
    )
    scope = CharField(
        required=False,
        default=DEFAULT_SCOPE,
        help_text="The scope of the access request. Defaults to 'read write'."
    )

# Serializer for request validation
class LogoutSerializer(Serializer):
    token = CharField(required=True, help_text="The access token to be revoked.")


class ChangePasswordSerializer(Serializer):
    old_password = CharField(help_text="The current password of the user.", required=True)
    new_password = CharField(help_text="The new password the user wants to set.", required=True)


class PasswordResetSerializer(Serializer):
    email = EmailField(help_text="The email address of the user requesting a password reset.", required=True)


class SignupSerializer(Serializer):
    email = EmailField(help_text="User's email address", required=True)
    password = CharField(help_text="User's password", required=True)
    first_name = CharField(help_text="User's first name", required=True)
    last_name = CharField(help_text="User's last name", required=True)
    role = CharField(help_text="User's role", required=True)


class RefreshTokenSerializer(Serializer):
    refresh_token = CharField(help_text="The refresh token to generate a new access token.", required=True)
    client_id = CharField(help_text="The client ID of the application requesting the refresh token.", required=True)




