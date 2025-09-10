"""User dashboard module for meal ordering system."""

from nicegui import ui, app
from typing import Optional
from datetime import datetime, date, time
from decimal import Decimal
from app.services import DishService, CartService, OrderService, AuthenticationService
from app.models import CartItemCreate, OrderCreate, DeliveryType, OrderStatus


def create():
    """Create user dashboard pages."""

    async def check_auth() -> Optional[int]:
        """Check if user is authenticated and return user ID."""
        await ui.context.client.connected()
        user_id = app.storage.user.get("user_id")
        if not user_id:
            ui.navigate.to("/login")
            return None
        return user_id

    def create_header():
        """Create common header for user pages."""
        with ui.row().classes("w-full justify-between items-center bg-white shadow-sm p-4 mb-6"):
            ui.label("Meal Ordering System").classes("text-2xl font-bold text-gray-800")

            with ui.row().classes("gap-4"):
                ui.link("Menu", "/dashboard").classes("text-blue-600 hover:text-blue-800")
                ui.link("Cart", "/cart").classes("text-blue-600 hover:text-blue-800")
                ui.link("Orders", "/orders").classes("text-blue-600 hover:text-blue-800")
                ui.link("Profile", "/profile").classes("text-blue-600 hover:text-blue-800")
                ui.link("Logout", "/logout").classes("text-red-600 hover:text-red-800")

    @ui.page("/dashboard")
    async def dashboard():
        user_id = await check_auth()
        if not user_id:
            return

        create_header()

        with ui.column().classes("w-full max-w-6xl mx-auto p-6"):
            ui.label("Available Dishes").classes("text-3xl font-bold mb-6 text-gray-800")

            # Category filter
            dishes = DishService.get_available_dishes()
            categories = list(set(dish.category for dish in dishes))

            with ui.row().classes("mb-6 gap-4"):
                ui.label("Filter by category:").classes("text-lg font-medium")
                category_filter = ui.select(options=["All"] + categories, value="All").classes("min-w-48")

            # Dish grid container
            dish_container = ui.column().classes("w-full")

            def update_dishes():
                """Update dish display based on filter."""
                dish_container.clear()

                filtered_dishes = dishes
                if category_filter.value != "All":
                    filtered_dishes = [d for d in dishes if d.category == category_filter.value]

                with dish_container:
                    with ui.grid(columns=3).classes("w-full gap-6"):
                        for dish in filtered_dishes:
                            with ui.card().classes("p-4 shadow-md hover:shadow-lg transition-shadow"):
                                # Dish image placeholder
                                if dish.image_url:
                                    ui.image(dish.image_url).classes("w-full h-48 object-cover rounded mb-4")
                                else:
                                    with ui.element("div").classes(
                                        "w-full h-48 bg-gray-200 rounded mb-4 flex items-center justify-center"
                                    ):
                                        ui.icon("restaurant").classes("text-6xl text-gray-400")

                                ui.label(dish.name).classes("text-xl font-bold mb-2")
                                ui.label(f"${dish.price:.2f}").classes("text-lg text-green-600 font-semibold mb-2")
                                ui.label(dish.description).classes("text-gray-600 mb-2 text-sm")
                                ui.label(f"Category: {dish.category}").classes("text-gray-500 text-xs mb-2")
                                ui.label(f"Stock: {dish.stock_quantity}").classes("text-gray-500 text-xs mb-4")

                                if dish.stock_quantity > 0:
                                    with ui.row().classes("w-full justify-between items-center"):
                                        quantity_input = ui.number(
                                            label="Qty", value=1, min=1, max=dish.stock_quantity
                                        ).classes("w-20")

                                        ui.button(
                                            "Add to Cart", on_click=lambda d=dish, q=quantity_input: add_to_cart(d, q)
                                        ).classes("bg-blue-500 text-white px-4 py-2")
                                else:
                                    ui.label("Out of Stock").classes("text-red-500 font-semibold")

            def add_to_cart(dish, quantity_input):
                """Add dish to cart."""
                if not quantity_input.value or quantity_input.value <= 0:
                    ui.notify("Please enter a valid quantity", type="negative")
                    return

                cart_data = CartItemCreate(dish_id=dish.id, quantity=int(quantity_input.value))

                result = CartService.add_to_cart(user_id, cart_data)
                if result:
                    ui.notify(f"Added {quantity_input.value} x {dish.name} to cart", type="positive")
                    quantity_input.value = 1
                else:
                    ui.notify("Failed to add to cart. Check stock availability.", type="negative")

            # Initial load
            update_dishes()
            category_filter.on("value-change", lambda: update_dishes())

    @ui.page("/cart")
    async def cart():
        user_id = await check_auth()
        if not user_id:
            return

        create_header()

        with ui.column().classes("w-full max-w-4xl mx-auto p-6"):
            ui.label("Shopping Cart").classes("text-3xl font-bold mb-6 text-gray-800")

            cart_container = ui.column().classes("w-full")

            def refresh_cart():
                """Refresh cart display."""
                cart_container.clear()

                cart_items = CartService.get_cart_items(user_id)

                with cart_container:
                    if not cart_items:
                        ui.label("Your cart is empty").classes("text-gray-500 text-center text-lg py-8")
                        ui.link("Browse Menu", "/dashboard").classes("text-blue-600 text-center block")
                        return

                    total_amount = Decimal("0")

                    for cart_item in cart_items:
                        dish = DishService.get_dish_by_id(cart_item.dish_id)
                        if not dish:
                            continue

                        subtotal = dish.price * cart_item.quantity
                        total_amount += subtotal

                        with ui.card().classes("p-4 mb-4"):
                            with ui.row().classes("w-full justify-between items-center"):
                                with ui.column():
                                    ui.label(dish.name).classes("text-lg font-semibold")
                                    ui.label(f"${dish.price:.2f} each").classes("text-gray-600")
                                    ui.label(f"Subtotal: ${subtotal:.2f}").classes("text-green-600 font-semibold")

                                with ui.row().classes("gap-4 items-center"):
                                    quantity_input = ui.number(
                                        value=cart_item.quantity, min=1, max=dish.stock_quantity
                                    ).classes("w-20")

                                    ui.button(
                                        "Update",
                                        on_click=lambda item=cart_item, qty=quantity_input: update_quantity(item, qty),
                                    ).classes("bg-yellow-500 text-white px-3 py-1")

                                    ui.button("Remove", on_click=lambda item=cart_item: remove_item(item)).classes(
                                        "bg-red-500 text-white px-3 py-1"
                                    )

                    # Total and checkout
                    with ui.card().classes("p-6 bg-blue-50 mt-6"):
                        ui.label(f"Total: ${total_amount:.2f}").classes("text-2xl font-bold text-center mb-4")

                        if cart_items:
                            ui.button("Proceed to Checkout", on_click=show_checkout).classes(
                                "w-full bg-green-500 text-white py-3 text-lg"
                            )

            def update_quantity(cart_item, quantity_input):
                """Update cart item quantity."""
                if quantity_input.value and quantity_input.value > 0:
                    from app.models import CartItemUpdate

                    update_data = CartItemUpdate(quantity=int(quantity_input.value))
                    result = CartService.update_cart_item(user_id, cart_item.id, update_data)
                    if result:
                        ui.notify("Quantity updated", type="positive")
                        refresh_cart()
                    else:
                        ui.notify("Failed to update quantity", type="negative")

            def remove_item(cart_item):
                """Remove item from cart."""
                result = CartService.remove_from_cart(user_id, cart_item.id)
                if result:
                    ui.notify("Item removed from cart", type="positive")
                    refresh_cart()
                else:
                    ui.notify("Failed to remove item", type="negative")

            async def show_checkout():
                """Show checkout dialog."""
                with ui.dialog() as dialog, ui.card():
                    ui.label("Complete Your Order").classes("text-xl font-bold mb-4")

                    # Pickup time selection
                    ui.label("Pickup/Delivery Time:").classes("font-semibold mb-2")
                    pickup_date = ui.date(value=date.today().isoformat()).classes("mb-4")
                    pickup_time = ui.time(value="12:00").classes("mb-4")

                    # Delivery type
                    ui.label("Order Type:").classes("font-semibold mb-2")
                    delivery_type = ui.select(
                        options={DeliveryType.PICKUP: "Pickup", DeliveryType.DELIVERY: "Delivery"},
                        value=DeliveryType.PICKUP,
                    ).classes("mb-4")

                    # Remarks
                    ui.label("Special Instructions (Optional):").classes("font-semibold mb-2")
                    remarks = ui.textarea(placeholder="Any special requests...").classes("mb-4")

                    with ui.row().classes("gap-4"):
                        ui.button("Cancel", on_click=dialog.close).classes("bg-gray-500 text-white px-4 py-2")
                        ui.button(
                            "Place Order",
                            on_click=lambda: place_order(dialog, pickup_date, pickup_time, delivery_type, remarks),
                        ).classes("bg-green-500 text-white px-4 py-2")

                await dialog

            def place_order(dialog, pickup_date, pickup_time, delivery_type, remarks):
                """Place the order."""
                try:
                    # Combine date and time
                    from datetime import date as date_type

                    if isinstance(pickup_date.value, str):
                        date_obj = date_type.fromisoformat(pickup_date.value)
                    else:
                        date_obj = pickup_date.value
                    pickup_datetime = datetime.combine(date_obj, time.fromisoformat(pickup_time.value))

                    order_data = OrderCreate(
                        pickup_time=pickup_datetime, delivery_type=delivery_type.value, remarks=remarks.value or ""
                    )

                    order = OrderService.create_order_from_cart(user_id, order_data)

                    if order:
                        ui.notify("Order placed successfully!", type="positive")
                        dialog.close()
                        refresh_cart()
                        ui.navigate.to("/orders")
                    else:
                        ui.notify("Failed to place order. Please check cart and stock availability.", type="negative")

                except Exception as e:
                    ui.notify(f"Error placing order: {str(e)}", type="negative")

            # Initial load
            refresh_cart()

    @ui.page("/orders")
    async def orders():
        user_id = await check_auth()
        if not user_id:
            return

        create_header()

        with ui.column().classes("w-full max-w-6xl mx-auto p-6"):
            ui.label("Order History").classes("text-3xl font-bold mb-6 text-gray-800")

            user_orders = OrderService.get_user_orders(user_id)

            if not user_orders:
                ui.label("No orders found").classes("text-gray-500 text-center text-lg py-8")
                ui.link("Start Shopping", "/dashboard").classes("text-blue-600 text-center block")
                return

            for order in user_orders:
                with ui.card().classes("p-6 mb-6 shadow-md"):
                    with ui.row().classes("w-full justify-between items-start mb-4"):
                        with ui.column():
                            ui.label(f"Order #{order.id}").classes("text-xl font-bold")
                            ui.label(f"Ordered: {order.order_date.strftime('%Y-%m-%d %H:%M')}").classes("text-gray-600")
                            ui.label(f"Pickup: {order.pickup_time.strftime('%Y-%m-%d %H:%M')}").classes("text-gray-600")
                            ui.label(f"Type: {order.delivery_type.value.title()}").classes("text-gray-600")

                        with ui.column():
                            status_color = {
                                OrderStatus.PENDING: "text-yellow-600",
                                OrderStatus.CONFIRMED: "text-blue-600",
                                OrderStatus.PREPARING: "text-orange-600",
                                OrderStatus.READY: "text-green-600",
                                OrderStatus.COMPLETED: "text-green-800",
                                OrderStatus.CANCELLED: "text-red-600",
                            }.get(order.status, "text-gray-600")

                            ui.label(f"Status: {order.status.value.title()}").classes(f"font-semibold {status_color}")
                            ui.label(f"Total: ${order.total_amount:.2f}").classes("text-lg font-bold text-green-600")

                    if order.remarks:
                        ui.label(f"Instructions: {order.remarks}").classes("text-gray-600 italic mb-4")

                    # Order items
                    ui.label("Items:").classes("font-semibold mb-2")
                    with ui.column().classes("bg-gray-50 p-4 rounded"):
                        with ui.row().classes("w-full font-semibold text-gray-700 pb-2 border-b"):
                            ui.label("Dish").classes("flex-1")
                            ui.label("Qty").classes("w-16 text-center")
                            ui.label("Price").classes("w-24 text-right")
                            ui.label("Subtotal").classes("w-24 text-right")

                        # Get order items (simplified - in real app would be more efficient)
                        from app.database import get_session
                        from app.models import OrderItem
                        from sqlmodel import select

                        with get_session() as session:
                            order_items = session.exec(select(OrderItem).where(OrderItem.order_id == order.id)).all()

                            for item in order_items:
                                dish = DishService.get_dish_by_id(item.dish_id)
                                if dish:
                                    with ui.row().classes("w-full py-2"):
                                        ui.label(dish.name).classes("flex-1")
                                        ui.label(str(item.quantity)).classes("w-16 text-center")
                                        ui.label(f"${item.unit_price:.2f}").classes("w-24 text-right")
                                        ui.label(f"${item.subtotal:.2f}").classes("w-24 text-right")

    @ui.page("/profile")
    async def profile():
        user_id = await check_auth()
        if not user_id:
            return

        create_header()

        user = AuthenticationService.get_user_by_id(user_id)
        if not user:
            ui.notify("User not found", type="negative")
            ui.navigate.to("/login")
            return

        with ui.column().classes("w-full max-w-2xl mx-auto p-6"):
            ui.label("User Profile").classes("text-3xl font-bold mb-6 text-gray-800")

            with ui.card().classes("p-6 shadow-md"):
                ui.label("Profile Information").classes("text-xl font-semibold mb-4")

                with ui.column().classes("gap-4"):
                    ui.label(f"Name: {user.name}").classes("text-lg")
                    ui.label(f"Email: {user.email}").classes("text-lg")
                    ui.label(f"Phone: {user.phone}").classes("text-lg")

                    if user.department:
                        ui.label(f"Department: {user.department.name}").classes("text-lg")
                    else:
                        ui.label("Department: Not assigned").classes("text-lg text-gray-500")

                    ui.label(f"Role: {user.role.value.title()}").classes("text-lg")
                    ui.label(f"Member since: {user.created_at.strftime('%Y-%m-%d')}").classes("text-lg text-gray-600")

                ui.separator().classes("my-6")

                ui.label("Note: To update your profile information, please contact an administrator.").classes(
                    "text-sm text-gray-500 italic"
                )
