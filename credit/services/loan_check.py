from datetime import date
from django.db.models import Sum
from credit.models import LoanData
from credit.models import CustomerData


def loan_checker(customer_id, loan_amount, interest_rate, tenure):
    today = date.today()

    customer = CustomerData.objects.get(id=customer_id)

    loans = LoanData.objects.filter(customer=customer)
    current_loans = loans.filter(end_date__gte=today)

    total_current_loan_amount = (
        current_loans.aggregate(total=Sum("loan_amount"))["total"] or 0
    )

    total_current_emi = (
        current_loans.aggregate(total=Sum("monthly_repayment"))["total"] or 0
    )
    if total_current_loan_amount > customer.approved_limit:
        return _reject(customer_id, tenure)

    if total_current_emi > 0.5 * customer.monthly_salary:
        return _reject(customer_id, tenure)

    credit_score = 0
    total_emis = sum(loan.tenure for loan in loans)
    paid_on_time = sum(loan.EMIs_paid_on_time for loan in loans)

    if total_emis > 0:
        emi_ratio = paid_on_time / total_emis
        credit_score += int(emi_ratio * 40)
    loan_count = loans.count()
    if loan_count <= 2:
        credit_score += 15
    elif loan_count <= 5:
        credit_score += 10
    else:
        credit_score += 5

    current_year_loans = loans.filter(start_date__year=today.year).count()
    if current_year_loans == 0:
        credit_score += 15
    elif current_year_loans <= 2:
        credit_score += 10
    else:
        credit_score += 5

    total_loan_volume = (
        loans.aggregate(total=Sum("loan_amount"))["total"] or 0
    )

    if total_loan_volume >= customer.approved_limit * 0.8:
        credit_score += 30
    elif total_loan_volume >= customer.approved_limit * 0.5:
        credit_score += 20
    else:
        credit_score += 10
    approval = False
    corrected_interest_rate = interest_rate

    if credit_score > 50:
        approval = True

    elif 30 < credit_score <= 50:
        approval = True
        corrected_interest_rate = max(interest_rate, 12)

    elif 10 < credit_score <= 30:
        approval = True
        corrected_interest_rate = max(interest_rate, 16)

    else:
        approval = False

    if tenure > 0:
        monthly_interest_rate = float(corrected_interest_rate) / (12 * 100)
        if monthly_interest_rate > 0:
            monthly_installment = loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate) ** tenure) / (((1 + monthly_interest_rate) ** tenure) - 1)
        else:
            monthly_installment = loan_amount / tenure
    else:
        monthly_installment = 0

    return {
        "customer_id": customer_id,
        "approval": approval,
        "interest_rate": float(interest_rate),
        "corrected_interest_rate": float(corrected_interest_rate),
        "tenure": tenure,
        "monthly_installment": round(monthly_installment, 2),
    }


def _reject(customer_id, tenure):
    return {
        "customer_id": customer_id,
        "approval": False,
        "interest_rate": None,
        "corrected_interest_rate": None,
        "tenure": tenure,
        "monthly_installment": None,
    }
