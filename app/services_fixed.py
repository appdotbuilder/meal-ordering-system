"""Simplified service layer for meal ordering system."""

import hashlib
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
from sqlmodel import select
from app.database import get_session
from app.models import (
    User,
    UserCreate,
    UserLogin,
    UserRole,
    Department,
    DepartmentCreate,
    DepartmentUpdate,
    Dish,
    DishCreate,
    DishUpdate,
    Order,
    OrderCreate,
    OrderItem,
    OrderStatus,
    CartItem,
    CartItemCreate,
)


class AuthenticationService:
    """Handle user authentication and registration."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def register_user(user_data: UserCreate) -> Optional[User]:
        """Register a new user."""
        with get_session() as session:
            # Check if email already exists
            existing_user = session.exec(select(User).where(User.email == user_data.email)).first()

            if existing_user:
                return None

            # Create new user
            user = User(
                name=user_data.name,
                email=user_data.email,
                password_hash=AuthenticationService.hash_password(user_data.password),
                phone=user_data.phone,
                department_id=user_data.department_id,
                role=UserRole.REGULAR,
            )

            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    @staticmethod
    def authenticate_user(login_data: UserLogin) -> Optional[User]:
        """Authenticate user with email and password."""
        with get_session() as session:
            user = session.exec(select(User).where(User.email == login_data.email)).first()

            if user and user.password_hash == AuthenticationService.hash_password(login_data.password):
                return user
            return None

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID."""
        with get_session() as session:
            return session.get(User, user_id)


class DepartmentService:
    """Manage departments."""

    @staticmethod
    def get_all_departments() -> List[Department]:
        """Get all active departments."""
        with get_session() as session:
            return list(session.exec(select(Department).where(Department.is_active)))

    @staticmethod
    def create_department(dept_data: DepartmentCreate) -> Optional[Department]:
        """Create a new department."""
        with get_session() as session:
            # Check if department name already exists
            existing = session.exec(select(Department).where(Department.name == dept_data.name)).first()

            if existing:
                return None

            department = Department(**dept_data.model_dump())
            session.add(department)
            session.commit()
            session.refresh(department)
            return department

    @staticmethod
    def update_department(dept_id: int, dept_data: DepartmentUpdate) -> Optional[Department]:
        """Update department information."""
        with get_session() as session:
            department = session.get(Department, dept_id)
            if not department:
                return None

            update_data = dept_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(department, field, value)

            department.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(department)
            return department

    @staticmethod
    def delete_department(dept_id: int) -> bool:
        """Soft delete a department."""
        with get_session() as session:
            department = session.get(Department, dept_id)
            if not department:
                return False

            department.is_active = False
            department.updated_at = datetime.utcnow()
            session.commit()
            return True


class DishService:
    """Manage dishes."""

    @staticmethod
    def get_available_dishes() -> List[Dish]:
        """Get all available dishes."""
        with get_session() as session:
            return list(session.exec(select(Dish).where(Dish.is_available)))

    @staticmethod
    def get_all_dishes() -> List[Dish]:
        """Get all dishes (for admin)."""
        with get_session() as session:
            return list(session.exec(select(Dish)))

    @staticmethod
    def get_dish_by_id(dish_id: int) -> Optional[Dish]:
        """Get dish by ID."""
        with get_session() as session:
            return session.get(Dish, dish_id)

    @staticmethod
    def create_dish(dish_data: DishCreate) -> Dish:
        """Create a new dish."""
        with get_session() as session:
            dish = Dish(**dish_data.model_dump())
            session.add(dish)
            session.commit()
            session.refresh(dish)
            return dish

    @staticmethod
    def update_dish(dish_id: int, dish_data: DishUpdate) -> Optional[Dish]:
        """Update dish information."""
        with get_session() as session:
            dish = session.get(Dish, dish_id)
            if not dish:
                return None

            update_data = dish_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(dish, field, value)

            dish.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(dish)
            return dish

    @staticmethod
    def delete_dish(dish_id: int) -> bool:
        """Soft delete a dish."""
        with get_session() as session:
            dish = session.get(Dish, dish_id)
            if not dish:
                return False

            dish.is_available = False
            dish.updated_at = datetime.utcnow()
            session.commit()
            return True


class CartService:
    """Manage shopping cart."""

    @staticmethod
    def get_cart_items(user_id: int) -> List[CartItem]:
        """Get all cart items for a user."""
        with get_session() as session:
            return list(session.exec(select(CartItem).where(CartItem.user_id == user_id)))

    @staticmethod
    def add_to_cart(user_id: int, cart_data: CartItemCreate) -> Optional[CartItem]:
        """Add item to cart or update quantity if exists."""
        with get_session() as session:
            # Check if dish is available and has enough stock
            dish = session.get(Dish, cart_data.dish_id)
            if not dish or not dish.is_available or dish.stock_quantity < cart_data.quantity:
                return None

            # Check if item already in cart
            existing_item = session.exec(
                select(CartItem).where(CartItem.user_id == user_id, CartItem.dish_id == cart_data.dish_id)
            ).first()

            if existing_item:
                # Update quantity
                new_quantity = existing_item.quantity + cart_data.quantity
                if new_quantity > dish.stock_quantity:
                    return None

                existing_item.quantity = new_quantity
                existing_item.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(existing_item)
                return existing_item
            else:
                # Create new cart item
                cart_item = CartItem(user_id=user_id, dish_id=cart_data.dish_id, quantity=cart_data.quantity)
                session.add(cart_item)
                session.commit()
                session.refresh(cart_item)
                return cart_item

    @staticmethod
    def clear_cart(user_id: int) -> bool:
        """Clear all items from user's cart."""
        with get_session() as session:
            cart_items = session.exec(select(CartItem).where(CartItem.user_id == user_id)).all()

            for item in cart_items:
                session.delete(item)

            session.commit()
            return True

    @staticmethod
    def get_cart_total(user_id: int) -> Decimal:
        """Calculate total amount in cart."""
        cart_items = CartService.get_cart_items(user_id)
        total = Decimal("0")

        with get_session() as session:
            for item in cart_items:
                dish = session.get(Dish, item.dish_id)
                if dish:
                    total += dish.price * item.quantity

        return total


class OrderService:
    """Manage orders."""

    @staticmethod
    def create_order_from_cart(user_id: int, order_data: OrderCreate) -> Optional[Order]:
        """Create order from user's cart."""
        with get_session() as session:
            # Get cart items
            cart_items = session.exec(select(CartItem).where(CartItem.user_id == user_id)).all()

            if not cart_items:
                return None

            # Calculate total
            total_amount = Decimal("0")
            order_items_data = []

            for cart_item in cart_items:
                dish = session.get(Dish, cart_item.dish_id)
                if not dish or not dish.is_available:
                    return None

                if dish.stock_quantity < cart_item.quantity:
                    return None

                subtotal = dish.price * cart_item.quantity
                total_amount += subtotal

                order_items_data.append(
                    {"dish_id": dish.id, "quantity": cart_item.quantity, "unit_price": dish.price, "subtotal": subtotal}
                )

            # Create order
            order = Order(
                user_id=user_id,
                pickup_time=order_data.pickup_time,
                delivery_type=order_data.delivery_type,
                total_amount=total_amount,
                remarks=order_data.remarks or "",
            )

            session.add(order)
            session.commit()
            session.refresh(order)

            # Create order items and update stock
            if order.id:
                for item_data in order_items_data:
                    order_item = OrderItem(order_id=order.id, **item_data)
                    session.add(order_item)

                    # Update stock
                    if item_data["dish_id"]:
                        dish = session.get(Dish, item_data["dish_id"])
                        if dish:
                            dish.stock_quantity -= item_data["quantity"]
                            dish.updated_at = datetime.utcnow()

                # Clear cart
                for cart_item in cart_items:
                    session.delete(cart_item)

                session.commit()
                session.refresh(order)

            return order

    @staticmethod
    def get_user_orders(user_id: int) -> List[Order]:
        """Get all orders for a user."""
        with get_session() as session:
            return list(session.exec(select(Order).where(Order.user_id == user_id)))

    @staticmethod
    def get_all_orders() -> List[Order]:
        """Get all orders (for admin)."""
        with get_session() as session:
            return list(session.exec(select(Order)))

    @staticmethod
    def get_order_by_id(order_id: int) -> Optional[Order]:
        """Get order by ID."""
        with get_session() as session:
            return session.get(Order, order_id)

    @staticmethod
    def update_order_status(order_id: int, status: OrderStatus) -> Optional[Order]:
        """Update order status."""
        with get_session() as session:
            order = session.get(Order, order_id)
            if not order:
                return None

            order.status = status
            order.updated_at = datetime.utcnow()
            session.commit()
            session.refresh(order)
            return order
