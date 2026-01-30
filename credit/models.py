from django.db import models

# Create your models here.


class CustomerData(models.Model):
    customer_id = models.IntegerField(unique=True)
    first_name = models.CharField(max_length =255)
    last_name = models.CharField(max_length =255)
    phone_number = models.CharField(unique=True,max_length =15)
    monthly_salary = models.IntegerField(null=False)
    approved_limit = models.IntegerField(null=False)
    current_debt = models.IntegerField(null=True)
    
    def __str__(self):
        return f"User {self.customer_id} has salary {self.monthly_salary} and debt {self.current_debt} "
    
    
    
class LoanData(models.Model):
    customer = models.ForeignKey("CustomerData",on_delete=models.CASCADE,related_name="loans")
    loan_id = models.IntegerField(null = False)
    loan_amount = models.IntegerField(null = False)
    tenure = models.IntegerField(null = False)
    interest_rate = models.DecimalField(null = False,max_digits = 4,decimal_places=2)
    monthly_repayment = models.IntegerField(null = False)
    EMIs_paid_on_time = models.IntegerField(null = False)
    start_date = models.DateField(null = False)
    end_date = models.DateField(null = False)
    