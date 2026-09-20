from django.contrib import admin

from .models import Category, Product, Order, OrderItem


# =========================
# CATEGORY ADMIN
# =========================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
    )

    search_fields = (
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


# =========================
# PRODUCT ADMIN
# =========================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "category",
        "price",
        "stock",
        "available",
        "created_at",
    )

    list_filter = (
        "category",
        "available",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    list_editable = (
        "price",
        "stock",
        "available",
    )

    ordering = (
        "-created_at",
    )


# =========================
# ORDER ITEM ADMIN
# =========================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "order",
        "product",
        "quantity",
        "price",
        "show_subtotal",
    )

    search_fields = (
        "product__name",
        "order__user__username",
    )

    list_filter = (
        "product",
    )

    @admin.display(
        description="Subtotal"
    )
    def show_subtotal(self, obj):
        return obj.subtotal()


# =========================
# ORDER ADMIN
# =========================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "phone",
        "city",
        "state",
        "pincode",
        "total_amount",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "state",
        "created_at",
    )

    search_fields = (
        "user__username",
        "phone",
        "address",
        "city",
        "state",
        "pincode",
    )

    readonly_fields = (
        "created_at",
    )

    list_editable = (
        "status",
    )

    ordering = (
        "-created_at",
    )

    fieldsets = (
        (
            "Order Information",
            {
                "fields": (
                    "user",
                    "total_amount",
                    "status",
                    "created_at",
                )
            },
        ),
        (
            "Delivery Information",
            {
                "fields": (
                    "phone",
                    "address",
                    "city",
                    "state",
                    "pincode",
                )
            },
        ),
    )