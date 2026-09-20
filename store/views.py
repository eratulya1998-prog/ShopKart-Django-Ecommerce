from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q

from .models import Category, Product, Order, OrderItem


# =========================
# HOME
# =========================

def home(request):

    products = Product.objects.filter(
        available=True
    )

    categories = Category.objects.all()

    # Search
    search_query = request.GET.get(
        "q",
        ""
    ).strip()

    if search_query:

        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    # Category filter
    category_slug = request.GET.get(
        "category",
        ""
    ).strip()

    if category_slug:

        products = products.filter(
            category__slug=category_slug
        )

    return render(
        request,
        "store/home.html",
        {
            "products": products,
            "categories": categories,
            "search_query": search_query,
            "selected_category": category_slug,
        }
    )


# =========================
# PRODUCT DETAILS
# =========================

def product_detail(request, slug):

    product = get_object_or_404(
        Product,
        slug=slug,
        available=True
    )

    return render(
        request,
        "store/product_detail.html",
        {
            "product": product
        }
    )


# =========================
# ADD TO CART
# =========================

def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        available=True
    )

    cart = request.session.get(
        "cart",
        {}
    )

    product_id_str = str(product_id)

    current_quantity = cart.get(
        product_id_str,
        0
    )

    if current_quantity < product.stock:

        cart[product_id_str] = (
            current_quantity + 1
        )

        messages.success(
            request,
            f"{product.name} added to your cart."
        )

    else:

        messages.warning(
            request,
            "Maximum available stock reached."
        )

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("store:cart")

# =========================
# UPDATE CART
# =========================

def update_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
        available=True
    )

    if request.method == "POST":

        action = request.POST.get("action")

        cart = request.session.get("cart", {})
        product_id_str = str(product_id)

        current_quantity = cart.get(product_id_str, 0)

        if action == "increase":

            if current_quantity < product.stock:

                cart[product_id_str] = current_quantity + 1

            else:

                messages.warning(
                    request,
                    f"Only {product.stock} units of "
                    f"{product.name} are available."
                )

        elif action == "decrease":

            if current_quantity > 1:

                cart[product_id_str] = current_quantity - 1

            elif product_id_str in cart:

                del cart[product_id_str]

        request.session["cart"] = cart
        request.session.modified = True

    return redirect("store:cart")

# =========================
# CART
# =========================

def cart(request):

    cart_data = request.session.get(
        "cart",
        {}
    )

    cart_items = []
    total = 0

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id,
            available=True
        )

        # Protect against invalid/old cart quantities
        if quantity > product.stock:
            quantity = product.stock

        if quantity <= 0:
            continue

        subtotal = (
            product.price * quantity
        )

        total += subtotal

        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    return render(
        request,
        "store/cart.html",
        {
            "cart_items": cart_items,
            "total": total,
        }
    )


# =========================
# REMOVE FROM CART
# =========================

def remove_from_cart(request, product_id):

    cart = request.session.get(
        "cart",
        {}
    )

    product_id_str = str(product_id)

    if product_id_str in cart:

        del cart[product_id_str]

    request.session["cart"] = cart
    request.session.modified = True

    messages.success(
        request,
        "Product removed from cart."
    )

    return redirect("store:cart")


# =========================
# REGISTER
# =========================

def register(request):

    if request.user.is_authenticated:

        return redirect("store:home")

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        email = request.POST.get(
            "email",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        confirm_password = request.POST.get(
            "confirm_password",
            ""
        )

        if not username or not email or not password:

            messages.error(
                request,
                "Please fill all required fields."
            )

            return render(
                request,
                "store/register.html"
            )

        if password != confirm_password:

            messages.error(
                request,
                "Passwords do not match."
            )

            return render(
                request,
                "store/register.html"
            )

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return render(
                request,
                "store/register.html"
            )

        if User.objects.filter(
            email=email
        ).exists():

            messages.error(
                request,
                "Email already registered."
            )

            return render(
                request,
                "store/register.html"
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        login(
            request,
            user
        )

        messages.success(
            request,
            "Registration successful!"
        )

        return redirect(
            "store:home"
        )

    return render(
        request,
        "store/register.html"
    )


# =========================
# LOGIN
# =========================

def login_view(request):

    if request.user.is_authenticated:

        return redirect(
            "store:home"
        )

    if request.method == "POST":

        username = request.POST.get(
            "username",
            ""
        ).strip()

        password = request.POST.get(
            "password",
            ""
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(
                request,
                user
            )

            messages.success(
                request,
                f"Welcome, {user.username}!"
            )

            # Respect ?next=... when provided
            next_url = request.GET.get(
                "next"
            )

            if next_url:

                return redirect(
                    next_url
                )

            return redirect(
                "store:home"
            )

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "store/login.html"
    )


# =========================
# LOGOUT
# =========================

def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have been logged out."
    )

    return redirect(
        "store:home"
    )


# =========================
# CHECKOUT
# =========================

@login_required(login_url="store:login")
def checkout(request):

    cart_data = request.session.get(
        "cart",
        {}
    )

    if not cart_data:

        messages.warning(
            request,
            "Your cart is empty."
        )

        return redirect(
            "store:cart"
        )

    cart_items = []
    total = 0

    # =========================
    # PREPARE CART
    # =========================

    for product_id, quantity in cart_data.items():

        product = get_object_or_404(
            Product,
            id=product_id,
            available=True
        )

        # Check stock
        if quantity > product.stock:

            messages.error(
                request,
                f"Only {product.stock} units of "
                f"{product.name} are available."
            )

            return redirect(
                "store:cart"
            )

        subtotal = (
            product.price * quantity
        )

        total += subtotal

        cart_items.append(
            {
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal,
            }
        )

    # =========================
    # PLACE ORDER
    # =========================

    if request.method == "POST":

        phone = request.POST.get(
            "phone",
            ""
        ).strip()

        address = request.POST.get(
            "address",
            ""
        ).strip()

        city = request.POST.get(
            "city",
            ""
        ).strip()

        state = request.POST.get(
            "state",
            ""
        ).strip()

        pincode = request.POST.get(
            "pincode",
            ""
        ).strip()

        # =========================
        # VALIDATION
        # =========================

        if not all(
            [
                phone,
                address,
                city,
                state,
                pincode,
            ]
        ):

            messages.error(
                request,
                "Please fill all delivery details."
            )

            return render(
                request,
                "store/checkout.html",
                {
                    "cart_items": cart_items,
                    "total": total,
                }
            )

        # Phone validation
        if not phone.isdigit() or len(phone) < 10:

            messages.error(
                request,
                "Please enter a valid phone number."
            )

            return render(
                request,
                "store/checkout.html",
                {
                    "cart_items": cart_items,
                    "total": total,
                }
            )

        # Pincode validation
        if not pincode.isdigit() or len(pincode) != 6:

            messages.error(
                request,
                "Please enter a valid 6-digit pincode."
            )

            return render(
                request,
                "store/checkout.html",
                {
                    "cart_items": cart_items,
                    "total": total,
                }
            )

        # =========================
        # CREATE ORDER
        # =========================

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            status="Pending",
            phone=phone,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
        )

        # =========================
        # CREATE ORDER ITEMS
        # =========================

        for item in cart_items:

            product = item["product"]
            quantity = item["quantity"]

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

            # Reduce stock
            product.stock -= quantity

            if product.stock == 0:

                product.available = False

            product.save()

        # =========================
        # CLEAR CART
        # =========================

        request.session["cart"] = {}
        request.session.modified = True

        messages.success(
            request,
            "Your order has been placed successfully!"
        )

        return redirect(
            "store:order_success",
            order_id=order.id
        )

    # =========================
    # CHECKOUT PAGE
    # =========================

    return render(
        request,
        "store/checkout.html",
        {
            "cart_items": cart_items,
            "total": total,
        }
    )


# =========================
# ORDER SUCCESS
# =========================

@login_required(login_url="store:login")
def order_success(
    request,
    order_id
):

    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(
        request,
        "store/order_success.html",
        {
            "order": order
        }
    )


# =========================
# MY ORDERS
# =========================

@login_required(login_url="store:login")
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related(
        "items__product"
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "store/my_orders.html",
        {
            "orders": orders
        }
    )