"""Seed initial demo data for meal ordering system."""

import logging
from decimal import Decimal
from app.services import AuthenticationService, DepartmentService, DishService
from app.models import UserCreate, DepartmentCreate, DishCreate, UserRole

logger = logging.getLogger(__name__)


def seed_demo_data():
    """Seed the database with demo data."""

    # Create departments
    departments_data = [
        DepartmentCreate(name="Engineering", description="Software development and IT"),
        DepartmentCreate(name="Marketing", description="Marketing and communications"),
        DepartmentCreate(name="Sales", description="Sales and customer relations"),
        DepartmentCreate(name="HR", description="Human resources"),
        DepartmentCreate(name="Finance", description="Financial operations"),
    ]

    departments = []
    for dept_data in departments_data:
        dept = DepartmentService.create_department(dept_data)
        if dept:
            departments.append(dept)
            logger.info(f"Created department: {dept.name}")

    # Create admin user
    admin_data = UserCreate(
        name="Admin User",
        email="admin@company.com",
        password="admin123",
        phone="555-0001",
        department_id=departments[0].id if departments else None,
    )

    admin_user = AuthenticationService.register_user(admin_data)
    if admin_user:
        # Update role to admin
        from app.database import get_session
        from app.models import User

        with get_session() as session:
            user = session.get(User, admin_user.id)
            if user:
                user.role = UserRole.ADMIN
                session.commit()
        logger.info("Created admin user: admin@company.com (password: admin123)")

    # Create regular users
    regular_users_data = [
        UserCreate(
            name="John Doe",
            email="john@company.com",
            password="password123",
            phone="555-0101",
            department_id=departments[0].id if departments else None,
        ),
        UserCreate(
            name="Jane Smith",
            email="jane@company.com",
            password="password123",
            phone="555-0102",
            department_id=departments[1].id if len(departments) > 1 else None,
        ),
        UserCreate(
            name="Mike Johnson",
            email="mike@company.com",
            password="password123",
            phone="555-0103",
            department_id=departments[2].id if len(departments) > 2 else None,
        ),
        UserCreate(
            name="Sarah Wilson",
            email="sarah@company.com",
            password="password123",
            phone="555-0104",
            department_id=departments[3].id if len(departments) > 3 else None,
        ),
    ]

    for user_data in regular_users_data:
        user = AuthenticationService.register_user(user_data)
        if user:
            logger.info(f"Created user: {user.email} (password: password123)")

    # Create dishes
    dishes_data = [
        # Pizza category
        DishCreate(
            name="Pizza Margherita",
            price=Decimal("15.99"),
            description="Classic pizza with tomato sauce, mozzarella cheese, and fresh basil",
            category="Pizza",
            stock_quantity=20,
            image_url="https://images.unsplash.com/photo-1604068549290-dea0e4a305ca?w=400",
        ),
        DishCreate(
            name="Pepperoni Pizza",
            price=Decimal("17.99"),
            description="Delicious pizza topped with pepperoni and mozzarella cheese",
            category="Pizza",
            stock_quantity=15,
            image_url="https://images.unsplash.com/photo-1628840042765-356cda07504e?w=400",
        ),
        DishCreate(
            name="Vegetarian Pizza",
            price=Decimal("16.99"),
            description="Fresh vegetables including bell peppers, mushrooms, onions, and olives",
            category="Pizza",
            stock_quantity=12,
            image_url="https://images.unsplash.com/photo-1571407970349-bc81e7e96d47?w=400",
        ),
        # Burger category
        DishCreate(
            name="Classic Cheeseburger",
            price=Decimal("12.99"),
            description="Juicy beef patty with cheese, lettuce, tomato, and pickles",
            category="Burger",
            stock_quantity=25,
            image_url="https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400",
        ),
        DishCreate(
            name="Chicken Burger",
            price=Decimal("11.99"),
            description="Grilled chicken breast with mayo, lettuce, and tomato",
            category="Burger",
            stock_quantity=20,
            image_url="https://images.unsplash.com/photo-1606755962773-d324e2013de5?w=400",
        ),
        DishCreate(
            name="Veggie Burger",
            price=Decimal("10.99"),
            description="Plant-based patty with avocado, sprouts, and special sauce",
            category="Burger",
            stock_quantity=15,
            image_url="https://images.unsplash.com/photo-1525059696034-4967a729002e?w=400",
        ),
        # Pasta category
        DishCreate(
            name="Spaghetti Carbonara",
            price=Decimal("14.99"),
            description="Creamy pasta with eggs, cheese, pancetta, and black pepper",
            category="Pasta",
            stock_quantity=18,
            image_url="https://images.unsplash.com/photo-1621996346565-e3dbc636d9ba?w=400",
        ),
        DishCreate(
            name="Penne Arrabbiata",
            price=Decimal("13.99"),
            description="Spicy tomato sauce with garlic, red chilies, and herbs",
            category="Pasta",
            stock_quantity=22,
            image_url="https://images.unsplash.com/photo-1551892374-ecf8754cf8b0?w=400",
        ),
        DishCreate(
            name="Fettuccine Alfredo",
            price=Decimal("15.99"),
            description="Rich and creamy white sauce with parmesan cheese",
            category="Pasta",
            stock_quantity=16,
            image_url="https://images.unsplash.com/photo-1645112411341-6c4fd023714a?w=400",
        ),
        # Salad category
        DishCreate(
            name="Caesar Salad",
            price=Decimal("9.99"),
            description="Romaine lettuce with parmesan, croutons, and Caesar dressing",
            category="Salad",
            stock_quantity=30,
            image_url="https://images.unsplash.com/photo-1546793665-c74683f339c1?w=400",
        ),
        DishCreate(
            name="Greek Salad",
            price=Decimal("10.99"),
            description="Mixed greens with feta cheese, olives, tomatoes, and olive oil",
            category="Salad",
            stock_quantity=25,
            image_url="https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400",
        ),
        DishCreate(
            name="Quinoa Power Bowl",
            price=Decimal("12.99"),
            description="Quinoa with roasted vegetables, chickpeas, and tahini dressing",
            category="Salad",
            stock_quantity=20,
            image_url="https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400",
        ),
        # Dessert category
        DishCreate(
            name="Chocolate Brownie",
            price=Decimal("6.99"),
            description="Rich chocolate brownie served warm with vanilla ice cream",
            category="Dessert",
            stock_quantity=35,
            image_url="https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=400",
        ),
        DishCreate(
            name="Tiramisu",
            price=Decimal("7.99"),
            description="Classic Italian dessert with coffee-soaked ladyfingers and mascarpone",
            category="Dessert",
            stock_quantity=15,
            image_url="https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=400",
        ),
        DishCreate(
            name="Cheesecake",
            price=Decimal("8.99"),
            description="New York style cheesecake with berry compote",
            category="Dessert",
            stock_quantity=20,
            image_url="https://images.unsplash.com/photo-1533134242443-d4fd215305ad?w=400",
        ),
        # Beverage category
        DishCreate(
            name="Fresh Orange Juice",
            price=Decimal("4.99"),
            description="Freshly squeezed orange juice",
            category="Beverage",
            stock_quantity=50,
            image_url="https://images.unsplash.com/photo-1621506289937-a8e4df240d0b?w=400",
        ),
        DishCreate(
            name="Iced Coffee",
            price=Decimal("3.99"),
            description="Cold brew coffee served over ice",
            category="Beverage",
            stock_quantity=40,
            image_url="https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400",
        ),
        DishCreate(
            name="Smoothie Bowl",
            price=Decimal("8.99"),
            description="Mixed berry smoothie topped with granola and fresh fruit",
            category="Beverage",
            stock_quantity=25,
            image_url="https://images.unsplash.com/photo-1511690656952-34342bb7c2f2?w=400",
        ),
    ]

    for dish_data in dishes_data:
        dish = DishService.create_dish(dish_data)
        if dish:
            logger.info(f"Created dish: {dish.name} - ${dish.price}")

    logger.info("Demo data seeded successfully!")
    logger.info("Login credentials:")
    logger.info("Admin: admin@company.com / admin123")
    logger.info("Users: john@company.com, jane@company.com, mike@company.com, sarah@company.com / password123")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_demo_data()
