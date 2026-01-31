from rest_framework import serializers
from credit.models import CustomerData


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
