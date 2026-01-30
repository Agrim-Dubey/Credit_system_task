from django.contrib import admin
from .models import CustomerData,LoanData
# Register your models here.
admin.site.register(CustomerData)
admin.site.register(LoanData)