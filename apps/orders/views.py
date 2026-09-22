from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.cart.cart import Cart
from apps.products.models import Product

from .models import Order, OrderItem
from .payments import MockPaymentGateway


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect("products:product_list")

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        shipping_address = request.POST.get("shipping_address", "").strip()
        card_number = request.POST.get("card_number", "").strip()

        if not full_name or not shipping_address or not card_number:
            messages.error(request, "Please fill in all fields.")
            return render(request, "orders/checkout.html", {"cart": cart})

        # Re-check stock at checkout time, not just when it was added to the cart -
        # someone else may have bought the last one in the meantime.
        cart_items = list(cart)
        for item in cart_items:
            product = Product.objects.get(pk=item["product"].pk)
            if item["quantity"] > product.stock:
                messages.error(
                    request,
                    f"Only {product.stock} of \"{product.name}\" left in stock - please update your cart.",
                )
                return redirect("cart:cart_detail")

        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                full_name=full_name,
                shipping_address=shipping_address,
                status=Order.Status.PENDING,
            )
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    product_name=item["product"].name,
                    price=item["price"],
                    quantity=item["quantity"],
                )

            result = MockPaymentGateway.charge(card_number, order.total_price)
            order.payment_reference = result.reference

            if result.success:
                order.status = Order.Status.PAID
                order.save()
                # Only decrement stock once payment has actually gone through.
                for item in cart_items:
                    Product.objects.filter(pk=item["product"].pk).update(
                        stock=item["product"].stock - item["quantity"]
                    )
                cart.clear()
                messages.success(request, result.message)
                return redirect("orders:order_success", order_id=order.id)
            else:
                order.status = Order.Status.FAILED
                order.save()
                messages.error(request, result.message)
                return redirect("orders:checkout")

    return render(request, "orders/checkout.html", {"cart": cart})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status=Order.Status.PAID)
    return render(request, "orders/order_success.html", {"order": order})


@login_required
def order_history(request):
    orders = request.user.orders.prefetch_related("items")
    return render(request, "orders/order_history.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/order_detail.html", {"order": order})
