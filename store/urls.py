from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.home, name="home"),

    path(
        "product/<slug:slug>/",
        views.product_detail,
        name="product_detail"
    ),

    # Cart
    path(
        "cart/",
        views.cart,
        name="cart"
    ),

    path(
        "cart/add/<int:product_id>/",
        views.add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/remove/<int:product_id>/",
        views.remove_from_cart,
        name="remove_from_cart"
    ),

    # Authentication
    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    # Checkout
    path(
        "checkout/",
        views.checkout,
        name="checkout"
    ),

    path(
        "order-success/<int:order_id>/",
        views.order_success,
        name="order_success"
    ),

    path(
        "orders/",
        views.my_orders,
        name="my_orders"
    ),
]