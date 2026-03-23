from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.conf import settings
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens,
            'message': 'Account bana liya!'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email', '').lower().strip()
    password = request.data.get('password', '')

    if not email or not password:
        return Response({'error': 'Email aur password zaroori hai'}, status=400)

    try:
        user = User.objects.get(email=email)
        if user.check_password(password):
            tokens = get_tokens(user)
            return Response({
                'user': UserSerializer(user).data,
                'tokens': tokens,
            })
        return Response({'error': 'Galat password hai'}, status=400)
    except User.DoesNotExist:
        return Response({'error': 'Email registered nahi hai'}, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def google_login(request):
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests

    token = request.data.get('token')
    if not token:
        return Response({'error': 'Token missing'}, status=400)

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID
        )
        email = idinfo['email']
        name = idinfo.get('name', '')
        picture = idinfo.get('picture', '')
        google_id = idinfo['sub']

        first_name = name.split(' ')[0] if name else ''
        last_name = ' '.join(name.split(' ')[1:]) if ' ' in name else ''

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': first_name,
                'last_name': last_name,
                'avatar': picture,
                'google_id': google_id,
            }
        )

        if not created:
            user.avatar = picture
            user.save()

        tokens = get_tokens(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': tokens,
            'is_new': created,
        })
    except ValueError as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    return Response(UserSerializer(request.user).data)