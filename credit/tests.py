from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from credit.models import CustomerData, LoanData
from datetime import date
from dateutil.relativedelta import relativedelta


class CustomerRegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
    
    def test_register_customer_success(self):
        data = {"first_name": "Johny","last_name": "Depp","age": 30,"phone_number": "1234567890","monthly_salary": 50000
        }
        response = self.client.post('/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'John')
        self.assertEqual(response.data['approved_limit'], 50000 * 36)
    
    def test_register_customer_missing_fields(self):
        data = {"first_name": "John","age": 30}
        response = self.client.post('/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoanEligibilityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = CustomerData.objects.create(first_name="Jane",last_name="Smith",age=25,phone_number="9876543210",monthly_salary=60000,approved_limit=60000 * 36,current_debt=0)
    
    def test_check_eligibility_valid_customer(self):
        data = {"customer_id": self.customer.id,"loan_amount": 100000,"interest_rate": 10.5,"tenure": 12  }
        response = self.client.post('/check-eligibility/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('approval', response.data)
    
    def test_check_eligibility_invalid_customer(self):
        data = {"customer_id": 99999,"loan_amount": 100000,"interest_rate": 10.5,"tenure": 12 }
        response = self.client.post('/check-eligibility/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_check_eligibility_negative_loan_amount(self):
        data = {"customer_id": self.customer.id,"loan_amount": -50000,"interest_rate": 10.5,"tenure": 12 }
        response = self.client.post('/check-eligibility/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CreateLoanTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = CustomerData.objects.create( first_name="Bob",last_name="Johnson",age=35,phone_number="5555555555",monthly_salary=80000,approved_limit=80000 * 36,current_debt=0 )
    
    def test_create_loan_success(self):
        data = { "customer_id": self.customer.id,"loan_amount": 200000,"interest_rate": 12.0,"tenure": 24}
        response = self.client.post('/create-loan/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['loan_approved'])
        self.assertIsNotNone(response.data['loan_id'])
    
    def test_create_loan_invalid_tenure(self):
        data = { "customer_id": self.customer.id, "loan_amount": 200000, "interest_rate": 12.0,"tenure": 0
        }
        response = self.client.post('/create-loan/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ViewLoanTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = CustomerData.objects.create(first_name="Alice",last_name="Williams",
            age=28,
            phone_number="1111111111",
            monthly_salary=70000,
            approved_limit=70000 * 36,
            current_debt=0
        )
        self.loan = LoanData.objects.create( customer=self.customer,oan_id=1,loan_amount=150000,tenure=18,interest_rate=11.5,monthly_repayment=9000,EMIs_paid_on_time=5,start_date=date.today(),end_date=date.today() + relativedelta(months=18)
        )
    
    def test_view_loan_success(self):
        response = self.client.get(f'/view-loan/{self.loan.loan_id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['loan_id'], self.loan.loan_id)
    
    def test_view_loan_not_found(self):
        response = self.client.get('/view-loan/99999')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_view_customer_loans(self):
        response = self.client.get(f'/view-loans/{self.customer.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['loans']), 1)
        self.assertEqual(response.data['customer_id'], self.customer.id)