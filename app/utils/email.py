import logging
from typing import Optional

from sib_api_v3_sdk import (
    ApiClient,
    Configuration,
    TransactionalEmailsApi,
    SendSmtpEmail,
)
from sib_api_v3_sdk.rest import ApiException

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    sender_email: Optional[str] = None,
    sender_name: Optional[str] = None,
) -> None:
    """Kirim email menggunakan Brevo transactional API.

    Jika API key tidak tersedia, fungsi hanya akan mencatat log tanpa melempar error.
    """
    if not settings.brevo_api_key:
        logger.warning("Brevo API key belum disetel; email tidak dikirim.")
        return

    configuration = Configuration()
    configuration.api_key["api-key"] = settings.brevo_api_key

    api_client = ApiClient(configuration)
    api_instance = TransactionalEmailsApi(api_client)

    email = SendSmtpEmail(
        to=[{"email": to_email}],
        sender={
            "email": sender_email or settings.email_sender,
            "name": sender_name or settings.email_sender_name,
        },
        subject=subject,
        html_content=html_content,
    )

    try:
        api_instance.send_transac_email(email)
        logger.info("Email dikirim ke %s dengan subjek %s", to_email, subject)
    except ApiException as exc:
        logger.error("Gagal mengirim email ke %s: %s", to_email, exc, exc_info=True)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Kesalahan tak terduga saat mengirim email: %s", exc)

