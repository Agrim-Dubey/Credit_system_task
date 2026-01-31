from decimal import Decimal
import pandas as pd
from pathlib import Path
from credit.models import CustomerData, LoanData

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CUSTOMER_FILE = BASE_DIR / "data" / "customer_data.xlsx"
LOAN_FILE = BASE_DIR / "data" / "loan_data.xlsx"


def ingest_customers():
    df = pd.read_excel(CUSTOMER_FILE)
    created = 0

    for _, row in df.iterrows():
        CustomerData.objects.create(
            first_name=row["First Name"],
            last_name=row["Last Name"],
            age=int(row["Age"]),
            phone_number=str(row["Phone Number"]),
            monthly_salary=int(row["Monthly Salary"]),
            approved_limit=36 * int(row["Monthly Salary"]),
            current_debt=0,
        )
        created += 1

    return {"created": created, "total": len(df)}


def ingest_loans():
    df = pd.read_excel(LOAN_FILE)
    created = 0

    for _, row in df.iterrows():
        customer = CustomerData.objects.get(id=int(row["Customer ID"]))

        LoanData.objects.create(
            customer=customer,
            loan_id=int(row["Loan ID"]),
            loan_amount=int(row["Loan Amount"]),
            tenure=int(row["Tenure"]),
            interest_rate=Decimal(str(row["Interest Rate"])),
            monthly_repayment=int(row["Monthly payment"]),
            EMIs_paid_on_time=int(row["EMIs paid on Time"]),
            start_date=pd.to_datetime(row["Date of Approval"]).date(),
            end_date=pd.to_datetime(row["End Date"]).date(),
        )
        created += 1

    return {"created": created, "total": len(df)}
