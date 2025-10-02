from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated

from .serializers import UserRegisterSerializer, UserMiniSerializer
from rest_framework import status
from .documents import UserDocument
from .permissions import IsStaffOrSuperuser

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # this is in case we wanna add some fields from user data to show our client (frontend)
        token = super().get_token(user)
        token["email"] = user.email
        token["is_staff"] = user.is_staff
        token["is_superuser"] = user.is_superuser
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add user info to the response alongside tokens
        user = self.user
        data.update({
            "user": {
                "id": str(user.id),
                "email": user.email,
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
            }
        })
        return data


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserMiniSerializer(request.user).data)


class UserSearchView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrSuperuser]
    def get(self, request):
        query = request.GET.get('q', '')
        page = int(request.GET.get('page', 1))
        page_size = 10  # Fixed page size

        if not query:
            return Response({'results': [], 'total': 0}, status=status.HTTP_200_OK)

        s = UserDocument.search().query(
            'multi_match',
            query=query,
            fields=['email', 'first_name', 'last_name'],
            fuzziness='AUTO'
        )

        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        results = s[start:end].execute()
        total = results.hits.total.value

        users = [
            {
                'id': hit.id,
                'email': hit.email,
                'first_name': hit.first_name,
                'last_name': hit.last_name,
            }
            for hit in results
        ]

        return Response({'results': users, 'total': total, 'page': page, 'page_size': page_size}, status=status.HTTP_200_OK)
