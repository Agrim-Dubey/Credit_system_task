from celery import shared_task
from credit.services.ingest_excel import ingest_customers,ingest_loans


@shared_task(bind=True)
def ingest_customers_task(self):
    try:
        result = ingest_customers()
        return {
            "status": "success",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
        }


@shared_task(bind=True)
def ingest_loans_task(self):
    try:
        result = ingest_loans()
        return {
            "status": "success",
            "result": result,
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
        }
