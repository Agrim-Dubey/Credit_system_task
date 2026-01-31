import pandas as pd
from pathlib import Path
from credit.models import CustomerData

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CUSTOMER_FILE = BASE_DIR / "data" / "customer_data.xlsx"


def ingest_customers():
    df = pd.read_excel(CUSTOMER_FILE)

    created = 0
    skipped = 0

    for _, row in df.iterrows():
        obj, is_created = CustomerData.objects.get_or_create(
            customer_id=int(row["Customer ID"]),
            defaults={
                "first_name": row["First Name"],
                "last_name": row["Last Name"],
                "age": int(row["Age"]),
                "phone_number": str(row["Phone Number"]),
                "monthly_salary": int(row["Monthly Salary"]),
                "approved_limit": int(row["Approved Limit"]),
                "current_debt": 0,
            },
        )

        if is_created:
            created += 1
        else:
            skipped += 1

    return {
        "created": created,
        "skipped": skipped,
        "total": len(df),
    }
