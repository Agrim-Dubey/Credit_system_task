from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from credit.services.loan_check import loan_checker
from .serializers import CustomerRegisterInputSerializer,CustomerRegisterOutputSerializer,LoanCheckInputSerializer,LoanCheckOutputSerializer
# Create your views here.


class RegisterCustomer(APIView):
    def post(self,request):
        serializer = CustomerRegisterInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        customer  =serializer.save()
        response_serializer = CustomerRegisterOutputSerializer(customer)
        return Response(response_serializer.data,staus=status.HTTP_201_CREATED)
    
class EligibiltyCheck(APIView):
    def post(self,request):
        serializer = LoanCheckInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        customer_id =serializer.validated_data["customer_id"]
        loan_amount =serializer.validated_data["loan_amount"]
        interest_rate = serializer.validated_data["interest_rate"]
        tenure = serializer.validated_data["tenure"]
        
        result = loan_checker(customer_id,loan_amount,interest_rate,tenure)
        fin_result = LoanCheckOutputSerializer(result)
        return Response(fin_result.data,status=status.HTTP_200_OK)