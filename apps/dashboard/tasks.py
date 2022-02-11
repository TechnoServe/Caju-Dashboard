from celery.utils.log import get_task_logger
from celery import shared_task
from .scripts.get_qar_information import get_qar_data_from_db
from .scripts.get_qar_information import QarObject

logger = get_task_logger(__name__)


def make_hashable(qars: list):
    return {
        item.document_id: item.dump()
        for item in qars
    }


@shared_task
def get_qar_data_from_db_task():
    """sends an email when feedback form is filled successfully"""
    print("Sent feedback email")
    logger.info("Sent feedback email")

    return make_hashable(get_qar_data_from_db())
