from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import CustomerRegisterInputSerializer,CustomerRegisterOutputSerializer
# Create your views here.


class RegisterCustomer(APIView):
    def post(self,request):
        serializer = CustomerRegisterInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        customer  =serializer.save()
        response_serializer = CustomerRegisterOutputSerializer(customer)
        return Response(response_serializer.data,staus=status.HTTP_201_CREATED)