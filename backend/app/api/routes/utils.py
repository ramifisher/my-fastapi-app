from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr
from sqlmodel import func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import AppStats, Item, Message, User
from app.utils import generate_test_email, send_email

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    return True


@router.get(
    "/stats",
    dependencies=[Depends(get_current_active_superuser)],
)
def get_stats(session: SessionDep) -> AppStats:
    """
    Return basic application statistics (superuser only).
    """
    total_users = session.exec(select(func.count()).select_from(User)).one()
    active_users = session.exec(
        select(func.count()).select_from(User).where(User.is_active == True)  # noqa: E712
    ).one()
    total_items = session.exec(select(func.count()).select_from(Item)).one()
    return AppStats(
        total_users=total_users,
        active_users=active_users,
        total_items=total_items,
    )
