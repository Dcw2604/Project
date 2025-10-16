from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from .models import User

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.get_full_name() or user.username,
                    'role': user.role,
                }
            })
        return Response({'success': False, 'error': 'Invalid credentials'}, status=401)

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        role = request.data.get('role', 'student')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        if User.objects.filter(username=username).exists():
            return Response({'success': False, 'error': 'Username already exists'}, status=400)
        
        user = User.objects.create_user(
            username=username,
            password=password,
            role=role,
            first_name=first_name,
            last_name=last_name
        )
        login(request, user)
        return Response({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.get_full_name() or user.username,
                'role': user.role,
            }
        })

class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'success': True})

class CSRFTokenView(APIView):
    def get(self, request):
        from django.middleware.csrf import get_token
        return Response({'csrfToken': get_token(request)})

class MeView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'success': True,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'name': request.user.get_full_name() or request.user.username,
                    'role': request.user.role,
                }
            })
        return Response({'success': False}, status=401)