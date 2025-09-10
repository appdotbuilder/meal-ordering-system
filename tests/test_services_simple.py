"""Simple service tests for meal ordering system."""

import pytest
from decimal import Decimal
from app.database import reset_db
from app.services import AuthenticationService, DepartmentService, DishService
from app.models import UserCreate, DepartmentCreate, DishCreate


@pytest.fixture()
def new_db():
    """Reset database for each test."""
    reset_db()
    yield
    reset_db()


class TestBasicServices:
    """Test basic service functionality."""

    def test_password_hashing(self, new_db):
        """Test password hashing works."""
        password = "test123"
        hash1 = AuthenticationService.hash_password(password)
        hash2 = AuthenticationService.hash_password(password)

        assert hash1 == hash2
        assert hash1 != password
        assert len(hash1) == 64

    def test_create_department(self, new_db):
        """Test creating a department."""
        dept_data = DepartmentCreate(name="Engineering")
        department = DepartmentService.create_department(dept_data)

        assert department is not None
        assert department.name == "Engineering"
        assert department.is_active

    def test_create_dish(self, new_db):
        """Test creating a dish."""
        dish_data = DishCreate(name="Pizza", price=Decimal("15.99"), category="Pizza", stock_quantity=10)

        dish = DishService.create_dish(dish_data)

        assert dish is not None
        assert dish.name == "Pizza"
        assert dish.price == Decimal("15.99")
        assert dish.category == "Pizza"
        assert dish.stock_quantity == 10
        assert dish.is_available

    def test_register_user(self, new_db):
        """Test user registration."""
        user_data = UserCreate(name="John Doe", email="john@example.com", password="password123", phone="123-456-7890")

        user = AuthenticationService.register_user(user_data)

        assert user is not None
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.phone == "123-456-7890"

    def test_authenticate_user(self, new_db):
        """Test user authentication."""
        # Register user first
        user_data = UserCreate(name="John Doe", email="john@example.com", password="password123", phone="123-456-7890")

        registered_user = AuthenticationService.register_user(user_data)
        assert registered_user is not None

        # Authenticate with correct password
        from app.models import UserLogin

        login_data = UserLogin(email="john@example.com", password="password123")
        authenticated_user = AuthenticationService.authenticate_user(login_data)

        assert authenticated_user is not None
        assert authenticated_user.email == "john@example.com"

        # Authenticate with wrong password
        wrong_login = UserLogin(email="john@example.com", password="wrongpassword")
        wrong_auth = AuthenticationService.authenticate_user(wrong_login)

        assert wrong_auth is None
