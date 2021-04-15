from django.contrib.auth import get_user_model, authenticate
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from UrlShortener_auth.serializers import RegisterSerializer, LoginSerializer

class Register(APIView):
    """
    The API to register a new user
    """
    parser_classes = (MultiPartParser, FormParser,)
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.on_valid_request_data(serializer.validated_data)

    def on_valid_request_data(self, data):
        phone = data.get('phone')
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')

        User = get_user_model()
        username = email

        with transaction.atomic():
            new_user = User.create_user(username=username, email=email, password=password, name=name, phone=phone)

        user_auth_token = new_user.auth_token

        return Response({
            'token': user_auth_token.key,
            'username': new_user.username
        }, status=status.HTTP_201_CREATED)


class Login(APIView):
    """
    The API for login
    """
    parser_classes = (MultiPartParser, FormParser,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.on_valid_request_data(serializer.validated_data)

    def on_valid_request_data(self, data):
        username = data['username']
        password = data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    'token': token.key
                },
                status=status.HTTP_200_OK)
        else:
            raise AuthenticationFailed()