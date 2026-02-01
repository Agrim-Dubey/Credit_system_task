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
# Create your views here.


class RegisterCustomer(APIView):
    throttle_classes =[ScopedRateThrottle]
    throttle_scope = "register"
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
            status=status.HTTP_201_CREATED,
        )


class ViewLoan(APIView):
    throttle_classes =[ScopedRateThrottle]
    throttle_scope = "view_loan"
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
    def get(self, request, customer_id):
        customer = CustomerData.objects.filter(id=customer_id).first()
        if not customer:
            return Response(
                {"detail": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        loans = customer.loans.all()
        serializer = ViewLoanSerializer(loans, many=True)

        return Response(
            {
                "customer_id": customer_id,
                "loans": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
        
        
        
        
        