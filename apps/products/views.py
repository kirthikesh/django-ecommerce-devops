from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.reviews.forms import ReviewForm

from .models import Category, Product


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category")

    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    category_slug = request.GET.get("category", "").strip()
    if category_slug:
        products = products.filter(category__slug=category_slug)

    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort = request.GET.get("sort")
    sort_map = {
        "price_asc": "price",
        "price_desc": "-price",
        "newest": "-created_at",
    }
    products = products.order_by(sort_map.get(sort, "-created_at"))

    categories = Category.objects.all()

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    querystring = request.GET.copy()
    querystring.pop("page", None)

    context = {
        "products": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
        "categories": categories,
        "query": query,
        "selected_category": category_slug,
        "sort": sort,
        "querystring": querystring.urlencode(),
    }
    return render(request, "products/product_list.html", context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.select_related("user").order_by("-created_at")

    user_can_review = (
        request.user.is_authenticated
        and not reviews.filter(user=request.user).exists()
    )

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to leave a review.")
            return redirect("accounts:login")
        form = ReviewForm(request.POST)
        if form.is_valid() and user_can_review:
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Thanks for your review!")
            return redirect("products:product_detail", slug=slug)
    else:
        form = ReviewForm()

    context = {
        "product": product,
        "reviews": reviews,
        "form": form,
        "user_can_review": user_can_review,
    }
    return render(request, "products/product_detail.html", context)
