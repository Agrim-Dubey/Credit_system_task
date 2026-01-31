from django.db import models


class CustomerData(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField()
    phone_number = models.CharField(unique=True, max_length=15)
    monthly_salary = models.IntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.IntegerField(default=0)

    def __str__(self):
        return f"Customer {self.id}"


class LoanData(models.Model):
    customer = models.ForeignKey(
        CustomerData,
        on_delete=models.CASCADE,
        related_name="loans"
    )
    loan_id = models.IntegerField()
    loan_amount = models.IntegerField()
    tenure = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=4, decimal_places=2)
    monthly_repayment = models.IntegerField()
    EMIs_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
