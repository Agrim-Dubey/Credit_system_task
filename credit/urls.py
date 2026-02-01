from django.urls import path
from .views import RegisterCustomer,EligibiltyCheck,CreateLoan,ViewLoan,ViewLoanForCustomer

urlpatterns = [
    path("register/", RegisterCustomer.as_view(), name="register"),
    path("check-eligibility/",EligibiltyCheck.as_view(),name="Eligibility_check"),
    path("create-loan/",CreateLoan.as_view(),name="Create-loan"),
    path("view-loan/<int:loan_id>",ViewLoan.as_view(),name="View-loan"),
    path("view-loans/<int:customer_id>",ViewLoanForCustomer.as_view(),name="Customer-loan-view")
    
]
