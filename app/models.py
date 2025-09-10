from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum


# Enums for type safety
class UserRole(str, Enum):
    REGULAR = "regular"
    ADMIN = "admin"


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DeliveryType(str, Enum):
    PICKUP = "pickup"
    DELIVERY = "delivery"


# Department model
class Department(SQLModel, table=True):
    __tablename__ = "departments"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    description: Optional[str] = Field(default="", max_length=500)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    users: List["User"] = Relationship(back_populates="department")


# User model
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    password_hash: str = Field(max_length=255)
    phone: str = Field(max_length=20)
    role: UserRole = Field(default=UserRole.REGULAR)
    department_id: Optional[int] = Field(default=None, foreign_key="departments.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    department: Optional[Department] = Relationship(back_populates="users")
    orders: List["Order"] = Relationship(back_populates="user")
    cart_items: List["CartItem"] = Relationship(back_populates="user")


# Dish model
class Dish(SQLModel, table=True):
    __tablename__ = "dishes"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=200)
    price: Decimal = Field(decimal_places=2, max_digits=10)
    description: str = Field(default="", max_length=1000)
    image_url: Optional[str] = Field(default=None, max_length=500)
    category: str = Field(max_length=100)
    stock_quantity: int = Field(default=0, ge=0)
    is_available: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    order_items: List["OrderItem"] = Relationship(back_populates="dish")
    cart_items: List["CartItem"] = Relationship(back_populates="dish")


# Order model
class Order(SQLModel, table=True):
    __tablename__ = "orders"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    order_date: datetime = Field(default_factory=datetime.utcnow)
    pickup_time: datetime
    delivery_type: DeliveryType = Field(default=DeliveryType.PICKUP)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    total_amount: Decimal = Field(decimal_places=2, max_digits=10)
    remarks: Optional[str] = Field(default="", max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(back_populates="order")


# Order item model (many-to-many between Order and Dish)
class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    dish_id: int = Field(foreign_key="dishes.id")
    quantity: int = Field(ge=1)
    unit_price: Decimal = Field(decimal_places=2, max_digits=10)
    subtotal: Decimal = Field(decimal_places=2, max_digits=10)

    # Relationships
    order: Order = Relationship(back_populates="order_items")
    dish: Dish = Relationship(back_populates="order_items")


# Cart item model (for shopping cart functionality)
class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    dish_id: int = Field(foreign_key="dishes.id")
    quantity: int = Field(ge=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="cart_items")
    dish: Dish = Relationship(back_populates="cart_items")


# Non-persistent schemas for validation and API


# User schemas
class UserCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8)
    phone: str = Field(max_length=20)
    department_id: Optional[int] = Field(default=None)


class UserUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    department_id: Optional[int] = Field(default=None)


class UserLogin(SQLModel, table=False):
    email: str = Field(max_length=255)
    password: str


# Department schemas
class DepartmentCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default="", max_length=500)


class DepartmentUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = Field(default=None)


# Dish schemas
class DishCreate(SQLModel, table=False):
    name: str = Field(max_length=200)
    price: Decimal = Field(decimal_places=2, max_digits=10)
    description: str = Field(default="", max_length=1000)
    image_url: Optional[str] = Field(default=None, max_length=500)
    category: str = Field(max_length=100)
    stock_quantity: int = Field(default=0, ge=0)


class DishUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=200)
    price: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=10)
    description: Optional[str] = Field(default=None, max_length=1000)
    image_url: Optional[str] = Field(default=None, max_length=500)
    category: Optional[str] = Field(default=None, max_length=100)
    stock_quantity: Optional[int] = Field(default=None, ge=0)
    is_available: Optional[bool] = Field(default=None)


# Order schemas
class OrderCreate(SQLModel, table=False):
    pickup_time: datetime
    delivery_type: DeliveryType = Field(default=DeliveryType.PICKUP)
    remarks: Optional[str] = Field(default="", max_length=1000)


class OrderUpdate(SQLModel, table=False):
    pickup_time: Optional[datetime] = Field(default=None)
    delivery_type: Optional[DeliveryType] = Field(default=None)
    status: Optional[OrderStatus] = Field(default=None)
    remarks: Optional[str] = Field(default=None, max_length=1000)


# Cart schemas
class CartItemCreate(SQLModel, table=False):
    dish_id: int
    quantity: int = Field(ge=1)


class CartItemUpdate(SQLModel, table=False):
    quantity: int = Field(ge=1)


# Order item schema
class OrderItemCreate(SQLModel, table=False):
    dish_id: int
    quantity: int = Field(ge=1)


# Summary schemas for reports
class DepartmentOrderSummary(SQLModel, table=False):
    department_id: int
    department_name: str
    total_orders: int
    total_quantity: int
    total_amount: Decimal


class DishOrderSummary(SQLModel, table=False):
    dish_id: int
    dish_name: str
    total_orders: int
    total_quantity: int
    total_amount: Decimal


# Order detail schema for admin viewing
class OrderDetail(SQLModel, table=False):
    order_id: int
    user_name: str
    user_email: str
    department_name: Optional[str]
    order_date: datetime
    pickup_time: datetime
    delivery_type: DeliveryType
    status: OrderStatus
    total_amount: Decimal
    remarks: Optional[str]
    items: List[Dict[str, Any]]  # List of order items with dish details
