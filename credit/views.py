from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import CustomerRegisterInputSerializer
# Create your views here.


class RegisterCustomer(APIView):
    def post(self,request):
        # serializer = CustomerRegisterInputSerializer(data=request.data)
        return None