from app.database import create_tables, get_session
from app.models import User
from sqlmodel import select
import app.homepage
import app.auth
import app.user_dashboard
import app.admin_dashboard


def startup() -> None:
    # this function is called before the first request
    create_tables()

    # Seed demo data if no users exist
    with get_session() as session:
        existing_users = session.exec(select(User)).first()
        if not existing_users:
            from app.seed_data import seed_demo_data

            seed_demo_data()

    # Register all modules
    app.homepage.create()
    app.auth.create()
    app.user_dashboard.create()
    app.admin_dashboard.create()
