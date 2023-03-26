from rest_framework import status, exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.authentication import get_authorization_header
from .models import User, UserToken
import jwt
from django.conf import settings


# Custom TokenAuthentication Class
class MyOwnTokenAuthentication(TokenAuthentication):

    def authenticate(self, request):
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'token':
            return None

        if len(auth) == 1:
            msg = {"status": status.HTTP_401_UNAUTHORIZED, 
                    "detail": "Invalid token header. No credentials provided.", "data": {}}
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = {"status": status.HTTP_401_UNAUTHORIZED, 
                    "detail": "Invalid token header.", "data": {}}
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1]
            if token=="null":
                msg = {"status": status.HTTP_401_UNAUTHORIZED, 
                    "detail": "Null token not allowed.", "data": {}}
                raise exceptions.AuthenticationFailed(msg)
        except UnicodeError:
            msg = {"status": status.HTTP_401_UNAUTHORIZED, 
                    "detail": "Invalid token header. Token string should not contain invalid characters.", 
                    "data": {}}
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        model = self.get_model()
        try:
            payload = jwt.decode(leeway=10, jwt=token, key=settings.SECRET_KEY, algorithms=['HS256'])
            id = payload['id']
            username = payload['username']
            try:
                try:
                    user = User.objects.get(id=id, username=username)
                except:
                    msg = {"status": status.HTTP_404_NOT_FOUND, "detail": "User Not Found", "data": {}}
                    raise exceptions.AuthenticationFailed(msg)
                try:
                    user_token = UserToken.objects.get(user=user, token=token)
                except:
                    msg = {"status": status.HTTP_404_NOT_FOUND, "detail": "Token Not Found", "data": {}}
                    raise exceptions.AuthenticationFailed(msg)

                if not str(token) == str(user_token.token):
                    msg = {"status": status.HTTP_401_UNAUTHORIZED, "detail": "Token Missmatch", "data": {}}
                    raise exceptions.AuthenticationFailed(msg)

            except User.DoesNotExist:
                msg = {"status" :status.HTTP_404_NOT_FOUND, "detail": "User Not Found", "data": {}}
                raise exceptions.AuthenticationFailed(msg)

        except (jwt.InvalidTokenError,jwt.DecodeError,jwt.ExpiredSignatureError):
            msg = {"status" :status.HTTP_401_UNAUTHORIZED, "detail": "Token is invalid or expire", "data": {}}
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)
