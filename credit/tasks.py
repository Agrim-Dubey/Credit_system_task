from celery import shared_task

from celery import shared_task
from credit.services.ingest_excel import ingest_customers


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
