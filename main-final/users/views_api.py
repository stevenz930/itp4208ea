from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny, 
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer
)
from .permissions import IsOwnerOrReadOnly

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def profile(self, request, pk=None):
        user = self.get_object()
        serializer = UserUpdateSerializer(
            user, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(user).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_password(self, request, pk=None):
        user = self.get_object()
        if not user.check_password(request.data.get('old_password')):
            return Response(
                {'old_password': 'Wrong password.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(request.data.get('new_password'))
        user.save()
        return Response({'status': 'password set'}, status=status.HTTP_200_OK)
