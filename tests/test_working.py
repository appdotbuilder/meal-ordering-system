"""Working tests for meal ordering system."""

import pytest
from decimal import Decimal
from app.database import reset_db
from app.services import AuthenticationService, DepartmentService, DishService, CartService
from app.models import UserCreate, DepartmentCreate, DishCreate, CartItemCreate


@pytest.fixture()
def new_db():
    """Reset database for each test."""
    reset_db()
    yield
    reset_db()


def test_authentication_flow(new_db):
    """Test user registration and authentication."""
    # Register user
    user_data = UserCreate(name="Test User", email="test@example.com", password="password123", phone="123-456-7890")

    user = AuthenticationService.register_user(user_data)
    assert user is not None
    assert user.name == "Test User"
    assert user.email == "test@example.com"

    # Authenticate user
    from app.models import UserLogin

    login_data = UserLogin(email="test@example.com", password="password123")
    auth_user = AuthenticationService.authenticate_user(login_data)

    assert auth_user is not None
    assert auth_user.email == "test@example.com"


def test_department_management(new_db):
    """Test department creation and management."""
    dept_data = DepartmentCreate(name="Engineering", description="Tech team")
    department = DepartmentService.create_department(dept_data)

    assert department is not None
    assert department.name == "Engineering"
    assert department.is_active

    # Get all departments
    departments = DepartmentService.get_all_departments()
    assert len(departments) == 1
    assert departments[0].name == "Engineering"


def test_dish_management(new_db):
    """Test dish creation and management."""
    dish_data = DishCreate(
        name="Test Pizza",
        price=Decimal("15.99"),
        description="Delicious test pizza",
        category="Pizza",
        stock_quantity=10,
    )

    dish = DishService.create_dish(dish_data)
    assert dish is not None
    assert dish.name == "Test Pizza"
    assert dish.price == Decimal("15.99")
    assert dish.category == "Pizza"
    assert dish.stock_quantity == 10

    # Get available dishes
    dishes = DishService.get_available_dishes()
    assert len(dishes) == 1
    assert dishes[0].name == "Test Pizza"


def test_cart_functionality(new_db):
    """Test shopping cart functionality."""
    # Create user
    user_data = UserCreate(name="Test User", email="test@example.com", password="password123", phone="123-456-7890")
    user = AuthenticationService.register_user(user_data)
    assert user is not None and user.id is not None

    # Create dish
    dish_data = DishCreate(name="Test Pizza", price=Decimal("15.99"), category="Pizza", stock_quantity=10)
    dish = DishService.create_dish(dish_data)
    assert dish is not None and dish.id is not None

    # Add to cart
    cart_data = CartItemCreate(dish_id=dish.id, quantity=2)
    cart_item = CartService.add_to_cart(user.id, cart_data)

    assert cart_item is not None
    assert cart_item.dish_id == dish.id
    assert cart_item.quantity == 2

    # Get cart items
    cart_items = CartService.get_cart_items(user.id)
    assert len(cart_items) == 1
    assert cart_items[0].quantity == 2

    # Get cart total
    total = CartService.get_cart_total(user.id)
    expected = dish.price * 2
    assert total == expected


def test_basic_system_integration(new_db):
    """Test basic system integration."""
    # Create department
    dept = DepartmentService.create_department(DepartmentCreate(name="Engineering"))
    assert dept is not None

    # Create user in department
    user_data = UserCreate(
        name="John Doe", email="john@example.com", password="password123", phone="123-456-7890", department_id=dept.id
    )
    user = AuthenticationService.register_user(user_data)
    assert user is not None
    assert user.department_id == dept.id

    # Create dishes
    pizza = DishService.create_dish(
        DishCreate(name="Pizza", price=Decimal("15.99"), category="Pizza", stock_quantity=5)
    )

    burger = DishService.create_dish(
        DishCreate(name="Burger", price=Decimal("12.99"), category="Burger", stock_quantity=3)
    )

    assert pizza is not None and burger is not None

    # Add items to cart
    if user.id and pizza.id and burger.id:
        CartService.add_to_cart(user.id, CartItemCreate(dish_id=pizza.id, quantity=2))
        CartService.add_to_cart(user.id, CartItemCreate(dish_id=burger.id, quantity=1))

        # Verify cart
        cart_items = CartService.get_cart_items(user.id)
        assert len(cart_items) == 2

        # Verify total
        expected_total = (pizza.price * 2) + (burger.price * 1)
        actual_total = CartService.get_cart_total(user.id)
        assert actual_total == expected_total


def test_password_security(new_db):
    """Test password hashing security."""
    password = "mysecretpassword"

    # Test hash consistency
    hash1 = AuthenticationService.hash_password(password)
    hash2 = AuthenticationService.hash_password(password)

    assert hash1 == hash2
    assert hash1 != password
    assert len(hash1) == 64  # SHA-256 hex digest length

    # Test different passwords produce different hashes
    different_hash = AuthenticationService.hash_password("differentpassword")
    assert hash1 != different_hash
