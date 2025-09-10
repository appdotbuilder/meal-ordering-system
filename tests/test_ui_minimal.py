"""Minimal UI smoke tests for meal ordering system."""

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
    # Should see some content without errors
    await user.should_see("Meal Ordering System")


async def test_login_page_loads(user: User, new_db) -> None:
    """Test login page loads without errors."""
    await user.open("/login")
    await user.should_see("Login")


async def test_register_page_loads(user: User, new_db) -> None:
    """Test register page loads without errors."""
    await user.open("/register")
    await user.should_see("Register")


async def test_logout_redirects(user: User, new_db) -> None:
    """Test logout redirects properly."""
    await user.open("/logout")
    await user.should_see("Login")


async def test_protected_routes_redirect(user: User, new_db) -> None:
    """Test protected routes redirect to login."""
    # Test dashboard redirect
    await user.open("/dashboard")
    await user.should_see("Login")

    # Test admin redirect
    await user.open("/admin")
    await user.should_see("Login")

    # Test cart redirect
    await user.open("/cart")
    await user.should_see("Login")
