from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.products.models import Product

from .cart import Cart


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get("quantity", 1))
    cart.add(product=product, quantity=quantity)
    messages.success(request, f"Added {product.name} to your cart.")
    return redirect("cart:cart_detail")


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))
    if quantity > 0:
        cart.add(product=product, quantity=quantity, update_quantity=True)
    else:
        cart.remove(product)
    return redirect("cart:cart_detail")


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"Removed {product.name} from your cart.")
    return redirect("cart:cart_detail")


def cart_detail(request):
    return render(request, "cart/cart_detail.html", {"cart": Cart(request)})
