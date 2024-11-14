from rest_framework import generics
from authentication.serializers import SignupSerializer


class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {'message': 'User created successfully!'}
        return response
