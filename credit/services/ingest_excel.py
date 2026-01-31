import pandas as pd 
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CUSTOMER_FILE  = BASE_DIR / "data" / "customer_data.xlsx"

def read_customer_file():
    df = pd.read_excel(CUSTOMER_FILE)
    return df 