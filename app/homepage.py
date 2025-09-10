"""Homepage module for meal ordering system."""

from nicegui import ui, app
from app.models import UserRole


def create():
    """Create homepage and redirect logic."""

    @ui.page("/")
    async def index():
        """Homepage with automatic redirect."""
        await ui.context.client.connected()

        user_id = app.storage.user.get("user_id")
        user_role = app.storage.user.get("user_role")

        if user_id:
            # User is logged in, redirect based on role
            if user_role == UserRole.ADMIN:
                ui.navigate.to("/admin")
            else:
                ui.navigate.to("/dashboard")
        else:
            # User not logged in, show welcome page
            with ui.column().classes("w-full min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100"):
                # Header
                with ui.row().classes("w-full justify-between items-center p-6 bg-white shadow-sm"):
                    ui.label("Meal Ordering System").classes("text-3xl font-bold text-gray-800")

                    with ui.row().classes("gap-4"):
                        ui.link("Login", "/login").classes(
                            "bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 no-underline"
                        )
                        ui.link("Register", "/register").classes(
                            "bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 no-underline"
                        )

                # Main content
                with ui.column().classes("flex-1 items-center justify-center text-center px-6"):
                    ui.label("Welcome to Our Meal Ordering System").classes("text-5xl font-bold text-gray-800 mb-6")
                    ui.label("Order delicious meals for pickup or delivery").classes("text-xl text-gray-600 mb-8")

                    # Features
                    with ui.row().classes("gap-8 max-w-4xl mx-auto mb-12"):
                        with ui.card().classes("p-6 text-center shadow-lg flex-1"):
                            ui.icon("restaurant_menu").classes("text-6xl text-blue-500 mb-4")
                            ui.label("Browse Menu").classes("text-xl font-semibold mb-2")
                            ui.label("Explore our variety of delicious dishes").classes("text-gray-600")

                        with ui.card().classes("p-6 text-center shadow-lg flex-1"):
                            ui.icon("shopping_cart").classes("text-6xl text-green-500 mb-4")
                            ui.label("Easy Ordering").classes("text-xl font-semibold mb-2")
                            ui.label("Add items to cart and place orders quickly").classes("text-gray-600")

                        with ui.card().classes("p-6 text-center shadow-lg flex-1"):
                            ui.icon("schedule").classes("text-6xl text-orange-500 mb-4")
                            ui.label("Flexible Pickup").classes("text-xl font-semibold mb-2")
                            ui.label("Choose your preferred pickup or delivery time").classes("text-gray-600")

                    # Call to action
                    with ui.row().classes("gap-4"):
                        ui.link("Get Started - Register", "/register").classes(
                            "bg-green-500 text-white px-8 py-4 rounded-lg text-lg font-semibold "
                            "hover:bg-green-600 no-underline shadow-lg"
                        )
                        ui.link("Already have an account? Login", "/login").classes(
                            "bg-blue-500 text-white px-8 py-4 rounded-lg text-lg font-semibold "
                            "hover:bg-blue-600 no-underline shadow-lg"
                        )

                # Footer
                with ui.row().classes("w-full justify-center p-6 bg-gray-800 text-white"):
                    ui.label("© 2024 Meal Ordering System. All rights reserved.").classes("text-center")
