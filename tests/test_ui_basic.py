"""Basic UI integration tests."""

import pytest
from nicegui.testing import User
from app.database import reset_db

pytest_plugins = ["nicegui.testing.user_plugin"]


@pytest.fixture()
def new_db():
    """Reset database for each test."""
    reset_db()
    yield
    reset_db()


async def test_homepage_loads(user: User, new_db) -> None:
    """Test homepage loads without errors."""
    await user.open("/")
    await user.should_see("Meal Ordering System")


async def test_login_page_loads(user: User, new_db) -> None:
    """Test login page loads."""
    await user.open("/login")
    await user.should_see("Login")


async def test_register_page_loads(user: User, new_db) -> None:
    """Test register page loads."""
    await user.open("/register")
    await user.should_see("Register")


async def test_protected_routes_redirect(user: User, new_db) -> None:
    """Test protected routes redirect to login."""
    await user.open("/dashboard")
    await user.should_see("Login")

    await user.open("/admin")
    await user.should_see("Login")

    await user.open("/cart")
    await user.should_see("Login")
