from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from credit.models import CustomerData,LoanData
from rest_framework.response import Response
from credit.services.loan_check import loan_checker
from datetime import date
from dateutil.relativedelta import relativedelta
from rest_framework.throttling import ScopedRateThrottle
from .serializers import CustomerRegisterInputSerializer,CustomerRegisterOutputSerializer,LoanCheckInputSerializer,LoanCheckOutputSerializer,CreateLoanInputSerializer,CreateLoanOutputSerializer,DetailSerializer,ViewLoanSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Create your views here.


class RegisterCustomer(APIView):
    throttle_classes =[ScopedRateThrottle]
    throttle_scope = "register"
    
    @swagger_auto_schema(
        operation_description="Register a new customer with their personal and financial details",
        request_body=CustomerRegisterInputSerializer,
        responses={
            201: openapi.Response(
                description="Customer successfully registered",
                schema=CustomerRegisterOutputSerializer,
                examples={
                    "application/json": {
                        "id": 1,
                        "first_name": "John",
                        "last_name": "Doe",
                        "age": 30,
                        "phone_number": "9876543210",
                        "monthly_salary": 50000,
                        "approved_limit": 1800000
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request - Validation Error",
                examples={
                    "application/json": {
                        "first_name": ["This field is required."],
                        "monthly_salary": ["This field is required."]
                    }
                }
            )
        },
        tags=['Customer Management']
    )
    def post(self,request):
        serializer = CustomerRegisterInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        
        customer  =serializer.save()
        response_serializer = CustomerRegisterOutputSerializer(customer)
        return Response(response_serializer.data,status=status.HTTP_201_CREATED)
    
class EligibiltyCheck(APIView):
    throttle_classes =[ScopedRateThrottle]
    throttle_scope = "check_eligibility"
    
    @swagger_auto_schema(
        operation_description="Check loan eligibility for a customer based on their credit score and financial history",
        request_body=LoanCheckInputSerializer,
        responses={
            200: openapi.Response(
                description="Eligibility check completed",
                schema=LoanCheckOutputSerializer,
                examples={
                    "application/json": {
                        "customer_id": 1,
                        "approval": True,
                        "interest_rate": 12.5,
                        "corrected_interest_rate": 12.5,
                        "tenure": 24,
                        "monthly_installment": 4707.35
                    }
                }
            ),
            400: openapi.Response(
                description="Bad Request - Validation Error",
                examples={
                    "application/json": {
                        "customer_id": ["no such customer found"],
                        "loan_amount": ["Loan amount must be greater than 0"]
                    }
                }
            )
        },
        tags=['Loan Operations']
    )
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
    
class CreateLoan(APIView):
    throttle_classes =[ScopedRateThrottle]
    throttle_scope = "create_loan"
    
    @swagger_auto_schema(
        operation_description="Create a new loan for an eligible customer",
        request_body=CreateLoanInputSerializer,
        responses={
            201: openapi.Response(
                description="Loan created successfully",
                schema=CreateLoanOutputSerializer,
                examples={
                    "application/json": {
                        "loan_id": 101,
                        "customer_id": 1,
                        "loan_approved": True,
                        "message": "Loan approved",
                        "monthly_installment": 4707.35
                    }
                }
            ),
            200: openapi.Response(
                description="Loan not approved",
                schema=CreateLoanOutputSerializer,
                examples={
                    "application/json": {"loan_id": None,"customer_id": 1,"loan_approved": False,"message": "Loan not approved based on eligibility criteria","monthly_installment": None}}),400: openapi.Response(
                description="Bad Request - Validation Error",
                examples={
                    "application/json": {
                        "customer_id": ["Customer does not exist"],
                        "loan_amount": ["Loan amount must be greater than 0"]}})},tags=['Loan Operations'])
    def post(self, request):
        serializer = CreateLoanInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        result = loan_checker(**data)

        if not result["approval"]:
            return Response(
                CreateLoanOutputSerializer({"loan_id": None,"customer_id": data["customer_id"],"loan_approved": False,"message": "Loan not approved based on eligibility criteria","monthly_installment": None,}).data,
                status=status.HTTP_200_OK,
            )
        customer = CustomerData.objects.get(id=data["customer_id"])
        loan = LoanData.objects.create(customer=customer,loan_amount=data["loan_amount"],tenure=data["tenure"],interest_rate=result["corrected_interest_rate"],monthly_repayment=result["monthly_installment"],EMIs_paid_on_time=0,start_date=date.today(),end_date=date.today() + relativedelta(months=data["tenure"]),
        )
        customer.current_debt += data["loan_amount"]
        customer.save(update_fields=["current_debt"])
        return Response(
            CreateLoanOutputSerializer({"loan_id": loan.id,"customer_id": customer.id,"loan_approved": True,"message": "Loan approved","monthly_installment": result["monthly_installment"],}).data,
            status=status.HTTP_201_CREATED,)
class ViewLoan(APIView):
    throttle_classes =[ScopedRateThrottle]
    throttle_scope = "view_loan"
    
    @swagger_auto_schema(
        operation_description="Retrieve loan details by loan ID",
        manual_parameters=[
            openapi.Parameter(
                'loan_id',openapi.IN_PATH,description="Unique identifier for the loan",type=openapi.TYPE_INTEGER,required=True)],
        responses={
            200: openapi.Response(
                description="Loan details retrieved successfully",
                examples={
                    "application/json": {"loan_id": 101,"customer": {"id": 1,"first_name": "John","last_name": "Doe","phone_number": "9876543210","age": 30},"loan_amount": 100000,"interest_rate": 12.5,"monthly_installment": 4707.35,"tenure": 24}}),
            404: openapi.Response(
                description="Loan not found",
                examples={"application/json": {"detail": "No loan with this loan id found"}})},tags=['Loan Operations'])
    def get(self, request, loan_id):
        loan = LoanData.objects.filter(loan_id=loan_id).select_related("customer").first()
        if not loan:
            return Response(
                {"detail": "No loan with this loan id found"},status=status.HTTP_404_NOT_FOUND,)
        customer_data = DetailSerializer(loan.customer).data
        return Response({"loan_id": loan.loan_id,"customer": customer_data,"loan_amount": loan.loan_amount,"interest_rate": loan.interest_rate,"monthly_installment": loan.monthly_repayment,"tenure": loan.tenure,},status=status.HTTP_200_OK,)
class ViewLoanForCustomer(APIView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "view_loan"
    
    @swagger_auto_schema(
        operation_description="Retrieve all loans for a specific customer",
        manual_parameters=[
            openapi.Parameter('customer_id',openapi.IN_PATH,description="Unique identifier for the customer",type=openapi.TYPE_INTEGER,required=True)],
        responses={
            200: openapi.Response(
                description="Customer loans retrieved successfully",
                examples={
                    "application/json": {
                        "customer_id": 1,
                        "loans": [{"loan_id": 101,"loan_amount": 100000,"interest_rate": 12.5,"monthly_repayment": 4707.35,"tenure": 24
                            },{"loan_id": 102,"loan_amount": 50000,"interest_rate": 10.0,"monthly_repayment": 2311.90,"tenure": 24}]}}),
            404: openapi.Response(
                description="Customer not found",
                examples={"application/json": {"detail": "Customer not found"}})},tags=['Loan Operations'])
    def get(self, request, customer_id):
        customer = CustomerData.objects.filter(id=customer_id).first()
        if not customer:
            return Response({"detail": "Customer not found"},status=status.HTTP_404_NOT_FOUND,)
        loans = customer.loans.all()
        serializer = ViewLoanSerializer(loans, many=True)
        return Response({"customer_id": customer_id,"loans": serializer.data,},status=status.HTTP_200_OK,)
        
        
        
        