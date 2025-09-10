"""Admin dashboard module for meal ordering system."""

from nicegui import ui, app
from decimal import Decimal
from app.services import DishService, DepartmentService, OrderService, AuthenticationService
from app.models import DishCreate, DishUpdate, DepartmentCreate, DepartmentUpdate, UserRole, OrderStatus


def create():
    """Create admin dashboard pages."""

    async def check_admin_auth() -> bool:
        """Check if user is authenticated as admin."""
        await ui.context.client.connected()
        user_id = app.storage.user.get("user_id")
        user_role = app.storage.user.get("user_role")

        if not user_id or user_role != UserRole.ADMIN:
            ui.navigate.to("/login")
            return False
        return True

    def create_admin_header():
        """Create common header for admin pages."""
        with ui.row().classes("w-full justify-between items-center bg-gray-800 text-white p-4 mb-6"):
            ui.label("Admin Dashboard").classes("text-2xl font-bold")

            with ui.row().classes("gap-4"):
                ui.link("Orders", "/admin").classes("text-white hover:text-gray-300")
                ui.link("Dishes", "/admin/dishes").classes("text-white hover:text-gray-300")
                ui.link("Departments", "/admin/departments").classes("text-white hover:text-gray-300")
                ui.link("Reports", "/admin/reports").classes("text-white hover:text-gray-300")
                ui.link("User View", "/dashboard").classes("text-yellow-300 hover:text-yellow-400")
                ui.link("Logout", "/logout").classes("text-red-300 hover:text-red-400")

    @ui.page("/admin")
    async def admin_orders():
        if not await check_admin_auth():
            return

        create_admin_header()

        with ui.column().classes("w-full max-w-7xl mx-auto p-6"):
            ui.label("Order Management").classes("text-3xl font-bold mb-6 text-gray-800")

            # Status filter
            with ui.row().classes("mb-6 gap-4"):
                ui.label("Filter by status:").classes("text-lg font-medium")
                status_filter = ui.select(
                    options=["All"] + [status.value for status in OrderStatus], value="All"
                ).classes("min-w-48")

            orders_container = ui.column().classes("w-full")

            def refresh_orders():
                """Refresh order display."""
                orders_container.clear()

                orders = OrderService.get_all_orders()

                # Filter by status
                if status_filter.value != "All":
                    orders = [o for o in orders if o.status.value == status_filter.value]

                with orders_container:
                    if not orders:
                        ui.label("No orders found").classes("text-gray-500 text-center text-lg py-8")
                        return

                    for order in orders:
                        user = AuthenticationService.get_user_by_id(order.user_id)
                        if not user:
                            continue

                        with ui.card().classes("p-6 mb-4 shadow-md"):
                            with ui.row().classes("w-full justify-between items-start mb-4"):
                                with ui.column().classes("flex-1"):
                                    ui.label(f"Order #{order.id}").classes("text-xl font-bold")
                                    ui.label(f"Customer: {user.name} ({user.email})").classes("text-gray-700")

                                    if user.department:
                                        ui.label(f"Department: {user.department.name}").classes("text-gray-600")

                                    ui.label(f"Ordered: {order.order_date.strftime('%Y-%m-%d %H:%M')}").classes(
                                        "text-gray-600"
                                    )
                                    ui.label(f"Pickup: {order.pickup_time.strftime('%Y-%m-%d %H:%M')}").classes(
                                        "text-gray-600"
                                    )
                                    ui.label(f"Type: {order.delivery_type.value.title()}").classes("text-gray-600")

                                with ui.column().classes("min-w-48"):
                                    # Status update
                                    status_select = ui.select(
                                        options={status: status.value.title() for status in OrderStatus},
                                        value=order.status,
                                    ).classes("mb-2")

                                    ui.button(
                                        "Update Status",
                                        on_click=lambda o=order, s=status_select: update_order_status(o, s),
                                    ).classes("w-full bg-blue-500 text-white")

                                    ui.label(f"Total: ${order.total_amount:.2f}").classes(
                                        "text-lg font-bold text-green-600 mt-2"
                                    )

                            if order.remarks:
                                ui.label(f"Instructions: {order.remarks}").classes("text-gray-600 italic mb-4")

                            # Order items
                            ui.label("Items:").classes("font-semibold mb-2")
                            with ui.column().classes("bg-gray-50 p-4 rounded"):
                                from app.database import get_session
                                from app.models import OrderItem
                                from sqlmodel import select

                                with get_session() as session:
                                    order_items = session.exec(
                                        select(OrderItem).where(OrderItem.order_id == order.id)
                                    ).all()

                                    for item in order_items:
                                        dish = DishService.get_dish_by_id(item.dish_id)
                                        if dish:
                                            with ui.row().classes("justify-between py-1"):
                                                ui.label(f"{dish.name} x {item.quantity}")
                                                ui.label(f"${item.subtotal:.2f}")

            def update_order_status(order, status_select):
                """Update order status."""
                result = OrderService.update_order_status(order.id, status_select.value)
                if result:
                    ui.notify(f"Order #{order.id} status updated", type="positive")
                    refresh_orders()
                else:
                    ui.notify("Failed to update order status", type="negative")

            # Initial load
            refresh_orders()
            status_filter.on("value-change", lambda: refresh_orders())

    @ui.page("/admin/dishes")
    async def admin_dishes():
        if not await check_admin_auth():
            return

        create_admin_header()

        with ui.column().classes("w-full max-w-7xl mx-auto p-6"):
            with ui.row().classes("w-full justify-between items-center mb-6"):
                ui.label("Dish Management").classes("text-3xl font-bold text-gray-800")
                add_dish_btn = ui.button("Add New Dish").classes("bg-green-500 text-white px-4 py-2")

            dishes_container = ui.column().classes("w-full")

            def refresh_dishes():
                """Refresh dish display."""
                dishes_container.clear()

                dishes = DishService.get_all_dishes()

                with dishes_container:
                    # Table headers
                    with ui.row().classes("w-full font-bold text-gray-700 pb-4 border-b mb-4"):
                        ui.label("Name").classes("flex-1")
                        ui.label("Category").classes("w-32")
                        ui.label("Price").classes("w-24 text-right")
                        ui.label("Stock").classes("w-24 text-center")
                        ui.label("Status").classes("w-24 text-center")
                        ui.label("Actions").classes("w-48 text-center")

                    for dish in dishes:
                        with ui.row().classes("w-full items-center py-3 border-b border-gray-200"):
                            with ui.column().classes("flex-1"):
                                ui.label(dish.name).classes("font-semibold")
                                if dish.description:
                                    ui.label(
                                        dish.description[:100] + ("..." if len(dish.description) > 100 else "")
                                    ).classes("text-sm text-gray-600")

                            ui.label(dish.category).classes("w-32")
                            ui.label(f"${dish.price:.2f}").classes("w-24 text-right")
                            ui.label(str(dish.stock_quantity)).classes("w-24 text-center")

                            status_color = "text-green-600" if dish.is_available else "text-red-600"
                            ui.label("Available" if dish.is_available else "Hidden").classes(
                                f"w-24 text-center {status_color}"
                            )

                            with ui.row().classes("w-48 justify-center gap-2"):
                                ui.button("Edit", on_click=lambda d=dish: show_edit_dish_dialog(d)).classes(
                                    "bg-yellow-500 text-white px-3 py-1 text-sm"
                                )

                                toggle_text = "Hide" if dish.is_available else "Show"
                                ui.button(toggle_text, on_click=lambda d=dish: toggle_dish_availability(d)).classes(
                                    "bg-gray-500 text-white px-3 py-1 text-sm"
                                )

            async def show_add_dish_dialog():
                """Show dialog to add new dish."""
                with ui.dialog() as dialog, ui.card().classes("w-96"):
                    ui.label("Add New Dish").classes("text-xl font-bold mb-4")

                    name_input = ui.input(label="Name*").classes("w-full mb-3")
                    category_input = ui.input(label="Category*").classes("w-full mb-3")
                    price_input = ui.number(label="Price*", format="%.2f", min=0.01).classes("w-full mb-3")
                    description_input = ui.textarea(label="Description").classes("w-full mb-3")
                    image_url_input = ui.input(label="Image URL").classes("w-full mb-3")
                    stock_input = ui.number(label="Stock Quantity*", value=0, min=0).classes("w-full mb-4")

                    with ui.row().classes("gap-4 justify-end"):
                        ui.button("Cancel", on_click=dialog.close).classes("bg-gray-500 text-white px-4 py-2")
                        ui.button(
                            "Add Dish",
                            on_click=lambda: add_dish(
                                dialog,
                                name_input,
                                category_input,
                                price_input,
                                description_input,
                                image_url_input,
                                stock_input,
                            ),
                        ).classes("bg-green-500 text-white px-4 py-2")

                await dialog

            def add_dish(
                dialog, name_input, category_input, price_input, description_input, image_url_input, stock_input
            ):
                """Add new dish."""
                if not all(
                    [
                        name_input.value,
                        category_input.value,
                        price_input.value is not None,
                        stock_input.value is not None,
                    ]
                ):
                    ui.notify("Please fill in all required fields", type="negative")
                    return

                dish_data = DishCreate(
                    name=name_input.value,
                    category=category_input.value,
                    price=Decimal(str(price_input.value)),
                    description=description_input.value or "",
                    image_url=image_url_input.value or None,
                    stock_quantity=int(stock_input.value),
                )

                dish = DishService.create_dish(dish_data)
                ui.notify(f'Dish "{dish.name}" added successfully', type="positive")
                dialog.close()
                refresh_dishes()

            async def show_edit_dish_dialog(dish):
                """Show dialog to edit dish."""
                with ui.dialog() as dialog, ui.card().classes("w-96"):
                    ui.label(f"Edit Dish: {dish.name}").classes("text-xl font-bold mb-4")

                    name_input = ui.input(label="Name*", value=dish.name).classes("w-full mb-3")
                    category_input = ui.input(label="Category*", value=dish.category).classes("w-full mb-3")
                    price_input = ui.number(label="Price*", value=float(dish.price), format="%.2f", min=0.01).classes(
                        "w-full mb-3"
                    )
                    description_input = ui.textarea(label="Description", value=dish.description).classes("w-full mb-3")
                    image_url_input = ui.input(label="Image URL", value=dish.image_url or "").classes("w-full mb-3")
                    stock_input = ui.number(label="Stock Quantity*", value=dish.stock_quantity, min=0).classes(
                        "w-full mb-4"
                    )

                    with ui.row().classes("gap-4 justify-end"):
                        ui.button("Cancel", on_click=dialog.close).classes("bg-gray-500 text-white px-4 py-2")
                        ui.button(
                            "Update Dish",
                            on_click=lambda: update_dish(
                                dialog,
                                dish,
                                name_input,
                                category_input,
                                price_input,
                                description_input,
                                image_url_input,
                                stock_input,
                            ),
                        ).classes("bg-blue-500 text-white px-4 py-2")

                await dialog

            def update_dish(
                dialog, dish, name_input, category_input, price_input, description_input, image_url_input, stock_input
            ):
                """Update dish."""
                dish_data = DishUpdate(
                    name=name_input.value if name_input.value != dish.name else None,
                    category=category_input.value if category_input.value != dish.category else None,
                    price=Decimal(str(price_input.value)) if price_input.value != float(dish.price) else None,
                    description=description_input.value if description_input.value != dish.description else None,
                    image_url=image_url_input.value if image_url_input.value != (dish.image_url or "") else None,
                    stock_quantity=int(stock_input.value) if stock_input.value != dish.stock_quantity else None,
                )

                result = DishService.update_dish(dish.id, dish_data)
                if result:
                    ui.notify(f'Dish "{dish.name}" updated successfully', type="positive")
                    dialog.close()
                    refresh_dishes()
                else:
                    ui.notify("Failed to update dish", type="negative")

            def toggle_dish_availability(dish):
                """Toggle dish availability."""
                dish_data = DishUpdate(is_available=not dish.is_available)
                result = DishService.update_dish(dish.id, dish_data)
                if result:
                    status = "shown" if not dish.is_available else "hidden"
                    ui.notify(f'Dish "{dish.name}" {status}', type="positive")
                    refresh_dishes()
                else:
                    ui.notify("Failed to update dish status", type="negative")

            # Set up button handlers
            add_dish_btn.on_click(show_add_dish_dialog)

            # Initial load
            refresh_dishes()

    @ui.page("/admin/departments")
    async def admin_departments():
        if not await check_admin_auth():
            return

        create_admin_header()

        with ui.column().classes("w-full max-w-5xl mx-auto p-6"):
            with ui.row().classes("w-full justify-between items-center mb-6"):
                ui.label("Department Management").classes("text-3xl font-bold text-gray-800")
                add_dept_btn = ui.button("Add New Department").classes("bg-green-500 text-white px-4 py-2")

            dept_container = ui.column().classes("w-full")

            def refresh_departments():
                """Refresh department display."""
                dept_container.clear()

                departments = DepartmentService.get_all_departments()

                with dept_container:
                    if not departments:
                        ui.label("No departments found").classes("text-gray-500 text-center text-lg py-8")
                        return

                    for dept in departments:
                        with ui.card().classes("p-4 mb-4 shadow-md"):
                            with ui.row().classes("w-full justify-between items-start"):
                                with ui.column().classes("flex-1"):
                                    ui.label(dept.name).classes("text-xl font-bold")
                                    if dept.description:
                                        ui.label(dept.description).classes("text-gray-600 mt-2")
                                    ui.label(f"Created: {dept.created_at.strftime('%Y-%m-%d')}").classes(
                                        "text-sm text-gray-500 mt-2"
                                    )

                                with ui.row().classes("gap-2"):
                                    ui.button("Edit", on_click=lambda d=dept: show_edit_dept_dialog(d)).classes(
                                        "bg-blue-500 text-white px-3 py-1"
                                    )

                                    ui.button("Deactivate", on_click=lambda d=dept: deactivate_department(d)).classes(
                                        "bg-red-500 text-white px-3 py-1"
                                    )

            async def show_add_dept_dialog():
                """Show dialog to add new department."""
                with ui.dialog() as dialog, ui.card().classes("w-96"):
                    ui.label("Add New Department").classes("text-xl font-bold mb-4")

                    name_input = ui.input(label="Department Name*").classes("w-full mb-3")
                    description_input = ui.textarea(label="Description").classes("w-full mb-4")

                    with ui.row().classes("gap-4 justify-end"):
                        ui.button("Cancel", on_click=dialog.close).classes("bg-gray-500 text-white px-4 py-2")
                        ui.button(
                            "Add Department", on_click=lambda: add_department(dialog, name_input, description_input)
                        ).classes("bg-green-500 text-white px-4 py-2")

                await dialog

            def add_department(dialog, name_input, description_input):
                """Add new department."""
                if not name_input.value:
                    ui.notify("Please enter department name", type="negative")
                    return

                dept_data = DepartmentCreate(name=name_input.value, description=description_input.value or "")

                result = DepartmentService.create_department(dept_data)
                if result:
                    ui.notify(f'Department "{result.name}" added successfully', type="positive")
                    dialog.close()
                    refresh_departments()
                else:
                    ui.notify("Failed to add department. Name may already exist.", type="negative")

            async def show_edit_dept_dialog(dept):
                """Show dialog to edit department."""
                with ui.dialog() as dialog, ui.card().classes("w-96"):
                    ui.label(f"Edit Department: {dept.name}").classes("text-xl font-bold mb-4")

                    name_input = ui.input(label="Department Name*", value=dept.name).classes("w-full mb-3")
                    description_input = ui.textarea(label="Description", value=dept.description or "").classes(
                        "w-full mb-4"
                    )

                    with ui.row().classes("gap-4 justify-end"):
                        ui.button("Cancel", on_click=dialog.close).classes("bg-gray-500 text-white px-4 py-2")
                        ui.button(
                            "Update Department",
                            on_click=lambda: update_department(dialog, dept, name_input, description_input),
                        ).classes("bg-blue-500 text-white px-4 py-2")

                await dialog

            def update_department(dialog, dept, name_input, description_input):
                """Update department."""
                dept_data = DepartmentUpdate(
                    name=name_input.value if name_input.value != dept.name else None,
                    description=description_input.value
                    if description_input.value != (dept.description or "")
                    else None,
                )

                result = DepartmentService.update_department(dept.id, dept_data)
                if result:
                    ui.notify(f'Department "{dept.name}" updated successfully', type="positive")
                    dialog.close()
                    refresh_departments()
                else:
                    ui.notify("Failed to update department", type="negative")

            def deactivate_department(dept):
                """Deactivate department."""
                result = DepartmentService.delete_department(dept.id)
                if result:
                    ui.notify(f'Department "{dept.name}" deactivated', type="positive")
                    refresh_departments()
                else:
                    ui.notify("Failed to deactivate department", type="negative")

            # Set up button handlers
            add_dept_btn.on_click(show_add_dept_dialog)

            # Initial load
            refresh_departments()

    @ui.page("/admin/reports")
    async def admin_reports():
        if not await check_admin_auth():
            return

        create_admin_header()

        with ui.column().classes("w-full max-w-7xl mx-auto p-6"):
            ui.label("Reports & Analytics").classes("text-3xl font-bold mb-6 text-gray-800")

            # Simplified reports - basic order count
            ui.label("Basic Statistics").classes("text-2xl font-semibold mb-4 text-gray-700")

            # Get basic stats
            all_orders = OrderService.get_all_orders()
            all_dishes = DishService.get_all_dishes()
            all_departments = DepartmentService.get_all_departments()

            with ui.card().classes("p-6 mb-8 shadow-md"):
                with ui.row().classes("gap-8"):
                    with ui.column().classes("items-center"):
                        ui.label(str(len(all_orders))).classes("text-3xl font-bold text-blue-600")
                        ui.label("Total Orders").classes("text-gray-600")

                    with ui.column().classes("items-center"):
                        ui.label(str(len(all_dishes))).classes("text-3xl font-bold text-green-600")
                        ui.label("Total Dishes").classes("text-gray-600")

                    with ui.column().classes("items-center"):
                        ui.label(str(len(all_departments))).classes("text-3xl font-bold text-purple-600")
                        ui.label("Active Departments").classes("text-gray-600")

            ui.label("Note: Detailed analytics coming soon!").classes("text-gray-500 italic")
