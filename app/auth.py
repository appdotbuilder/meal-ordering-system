"""Authentication module for meal ordering system."""

from nicegui import ui, app
from app.services import AuthenticationService, DepartmentService
from app.models import UserCreate, UserLogin, UserRole


def create():
    """Create authentication pages."""

    @ui.page("/login")
    async def login_page():
        # Wait for client connection to access storage
        await ui.context.client.connected()

        # Check if user is already logged in
        if app.storage.user.get("user_id"):
            ui.navigate.to("/dashboard")
            return

        with ui.column().classes("w-full max-w-md mx-auto mt-16 p-6"):
            ui.label("Login to Meal Ordering System").classes("text-3xl font-bold text-center mb-8 text-gray-800")

            with ui.card().classes("w-full p-8 shadow-lg"):
                ui.label("Sign In").classes("text-xl font-semibold mb-6 text-gray-700")

                email_input = ui.input(label="Email", placeholder="Enter your email").classes("w-full mb-4")

                password_input = ui.input(label="Password", placeholder="Enter your password", password=True).classes(
                    "w-full mb-6"
                )

                login_btn = ui.button("Sign In").classes("w-full bg-blue-500 text-white py-3 mb-4")

                ui.separator().classes("my-4")

                ui.label("Don't have an account?").classes("text-sm text-gray-600 text-center")
                ui.link("Register here", "/register").classes("text-blue-500 hover:text-blue-600 text-center block")

                async def handle_login():
                    if not email_input.value or not password_input.value:
                        ui.notify("Please fill in all fields", type="negative")
                        return

                    login_data = UserLogin(email=email_input.value, password=password_input.value)

                    user = AuthenticationService.authenticate_user(login_data)

                    if user:
                        # Store user session
                        app.storage.user["user_id"] = user.id
                        app.storage.user["user_name"] = user.name
                        app.storage.user["user_email"] = user.email
                        app.storage.user["user_role"] = user.role

                        ui.notify(f"Welcome, {user.name}!", type="positive")

                        # Redirect based on role
                        if user.role == UserRole.ADMIN:
                            ui.navigate.to("/admin")
                        else:
                            ui.navigate.to("/dashboard")
                    else:
                        ui.notify("Invalid email or password", type="negative")

                login_btn.on_click(handle_login)

    @ui.page("/register")
    async def register_page():
        await ui.context.client.connected()

        # Check if user is already logged in
        if app.storage.user.get("user_id"):
            ui.navigate.to("/dashboard")
            return

        with ui.column().classes("w-full max-w-md mx-auto mt-16 p-6"):
            ui.label("Create Account").classes("text-3xl font-bold text-center mb-8 text-gray-800")

            with ui.card().classes("w-full p-8 shadow-lg"):
                ui.label("Register").classes("text-xl font-semibold mb-6 text-gray-700")

                name_input = ui.input(label="Full Name", placeholder="Enter your full name").classes("w-full mb-4")

                email_input = ui.input(label="Email", placeholder="Enter your email").classes("w-full mb-4")

                phone_input = ui.input(label="Phone Number", placeholder="Enter your phone number").classes(
                    "w-full mb-4"
                )

                password_input = ui.input(
                    label="Password", placeholder="Create a password (min 8 characters)", password=True
                ).classes("w-full mb-4")

                confirm_password_input = ui.input(
                    label="Confirm Password", placeholder="Confirm your password", password=True
                ).classes("w-full mb-4")

                # Department selection
                departments = DepartmentService.get_all_departments()
                department_options = {dept.id: dept.name for dept in departments}
                department_select = ui.select(options=department_options, label="Department").classes("w-full mb-6")

                register_btn = ui.button("Create Account").classes("w-full bg-green-500 text-white py-3 mb-4")

                ui.separator().classes("my-4")

                ui.label("Already have an account?").classes("text-sm text-gray-600 text-center")
                ui.link("Sign in here", "/login").classes("text-blue-500 hover:text-blue-600 text-center block")

                async def handle_register():
                    # Validation
                    if not all(
                        [
                            name_input.value,
                            email_input.value,
                            phone_input.value,
                            password_input.value,
                            confirm_password_input.value,
                        ]
                    ):
                        ui.notify("Please fill in all fields", type="negative")
                        return

                    if len(password_input.value) < 8:
                        ui.notify("Password must be at least 8 characters long", type="negative")
                        return

                    if password_input.value != confirm_password_input.value:
                        ui.notify("Passwords do not match", type="negative")
                        return

                    if not department_select.value:
                        ui.notify("Please select a department", type="negative")
                        return

                    user_data = UserCreate(
                        name=name_input.value,
                        email=email_input.value,
                        phone=phone_input.value,
                        password=password_input.value,
                        department_id=department_select.value,
                    )

                    user = AuthenticationService.register_user(user_data)

                    if user:
                        ui.notify("Account created successfully! Please sign in.", type="positive")
                        ui.navigate.to("/login")
                    else:
                        ui.notify("Email already exists or registration failed", type="negative")

                register_btn.on_click(handle_register)

    @ui.page("/logout")
    async def logout():
        await ui.context.client.connected()

        # Clear user session
        app.storage.user.clear()
        ui.notify("You have been logged out", type="info")
        ui.navigate.to("/login")
