from django.shortcuts import render, get_object_or_404
from .models import Product, ProductAssociation, Category, SpecialOffer
from django.views import View
from django.db.models import Q
from datetime import datetime


class ProductDisplay(View):
    """
    Provides the user with a list of all products in the database. The list
    can be filtered by category. The list can also be filtered to match a
    search term provided by the user, where the search term appears either
    in the name or the description of the product.
    """

    def get(self, request):
        offers = None
        categories = Category.objects.all()
        products = Product.objects.all().order_by('category')\
                          .order_by('-stock_level')
        if 'category' in request.GET:
            selection = request.GET['category'].split(',')
            if 'all' not in selection:
                products = products.filter(category__name__in=selection)
        if 'search' in request.GET:
            search_term = request.GET['search']
            queries = Q(name__icontains=search_term) | \
                Q(description__icontains=search_term)
            products = products.filter(queries)

        # Get all special offers that are currently active
        now = datetime.now()
        queries = Q(start_date__lte=now) & Q(end_date__gte=now)
        offers = SpecialOffer.objects.filter(queries)
        context = {
            'products': products,
            'categories': categories,
            'special_offers': offers,
        }
        return render(request, 'products/product_display.html', context)


class ProductDetail(View):
    """
    Provides all available detail about a single product, and a list
    of the products associated with that product, ordered by weight
    """

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        # Get a list of any products associated with this one.
        associated_products = ProductAssociation.objects.filter(
            base_product=product
        ).order_by('-weight')
        p_list = [ap.associated_product for ap in associated_products]

        # Get any special offer applying to this product.
        now = datetime.now()
        queries = Q(start_date__lte=now) & Q(end_date__gte=now)
        special_offers = SpecialOffer.objects.filter(product=product) \
            .filter(queries).order_by('-start_date')
        offer = special_offers[0] if special_offers else None
        reduction = product.price - offer.reduced_price if offer else 0

        # Get quantity of product already in basket:
        basket = request.session.get('basket', {})
        print(basket)
        quantity_in_basket = basket.get(str(product.id), 0)
        quantity_available = product.stock_level - quantity_in_basket
        print(f'quantity available of {product.name} == {quantity_available}')

        context = {
            'product': product,
            'stock_level': product.stock_level,
            'max_quantity': min(quantity_available, 10),
            'associated_products': p_list,
            'offer': offer,
            'reduction': reduction,
        }
        return render(request, 'products/product_detail.html', context)
