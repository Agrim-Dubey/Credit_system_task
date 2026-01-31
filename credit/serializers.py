from rest_framework import serializers
from credit.models import CustomerData
from credit.models import LoanData


class CustomerRegisterInputSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomerData
        fields = ["first_name","last_name","age","phone_number","monthly_salary"]
    
    
    def create(self,validated_data):
        monthly_salary=validated_data["monthly_salary"]
        approved_limit = 36*monthly_salary
        
        customer = CustomerData.objects.create(**validated_data,approved_limit = approved_limit,current_debt=0)
        return customer
        
class CustomerRegisterOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerData
        fields = [
            "id",            
            "first_name",
            "last_name",
            "age",
            "phone_number",
            "monthly_salary",
            "approved_limit",
        ]

class LoanCheckInputSerializer(serializers.Serializer):
    customer_id=serializers.IntegerField(required = True)
    loan_amount = serializers.IntegerField(required = True)
    interest_rate = serializers.DecimalField(required=True)
    tenure = serializers.IntegerField(required = True)
    
    
    def validate_customer_id(self,value):
        if not CustomerData.objects.filter(id=value).exists():
            raise serializers.ValidationError("no such customer found")
        return value
    def validate_loan_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Loan amount must be greater than 0")
        return value

    def validate_interest_rate(self, value):
        if value <= 0 or value > 100:
            raise serializers.ValidationError("Interest rate must be between 0 and 100")
        return value

    def validate_tenure(self, value):
        if value <= 0:
            raise serializers.ValidationError("Tenure must be greater than 0")
        return value


class LoanCheckOutputSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.FloatField(allow_null=True)
    corrected_interest_rate = serializers.FloatField(allow_null=True)
    tenure = serializers.IntegerField()
    monthly_installment = serializers.FloatField(allow_null=True)
    
class CreateLoanInputSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(required=True)
    loan_amount = serializers.FloatField(required=True)
    interest_rate = serializers.FloatField(required=True)
    tenure = serializers.IntegerField(required=True)

    def validate_customer_id(self, value):
        if not CustomerData.objects.filter(id=value).exists():
            raise serializers.ValidationError("Customer does not exist")
        return value

    def validate_loan_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Loan amount must be greater than 0")
        return value

    def validate_interest_rate(self, value):
        if value <= 0 or value > 100:
            raise serializers.ValidationError("Interest rate must be between 0 and 100")
        return value

    def validate_tenure(self, value):
        if value <= 0:
            raise serializers.ValidationError("Tenure must be greater than 0")
        return value
    
class CreateLoanOutputSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField(allow_null=True)
    customer_id = serializers.IntegerField()
    loan_approved = serializers.BooleanField()
    message = serializers.CharField()
    monthly_installment = serializers.FloatField(allow_null=True)