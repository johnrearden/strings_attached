from django.shortcuts import render, get_object_or_404
from .models import Product, ProductAssociation, Category
from django.views import View
from django.db.models import Q


class ProductDisplay(View):
    """
    Blah
    """
    def get(self, request):
        categories = Category.objects.all()
        products = Product.objects.all().order_by('category')
        if 'category' in request.GET:
            selection = request.GET['category'].split(',')
            if 'all' not in selection:
                products = products.filter(category__name__in=selection)
        if 'search' in request.GET:
            search_term = request.GET['search']
            queries = Q(name__icontains=search_term) | \
                Q(description__icontains=search_term)
            products = products.filter(queries)
        context = {
            'products': products,
            'categories': categories,
        }
        return render(request, 'products/product_display.html', context)


class ProductDetail(View):
    """
    Provides all available detail about a single product, and a list
    of the products associated with that product, ordered by weight
    """
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        print(product)
        associated_products = ProductAssociation.objects.filter(
            base_product=product
            ).order_by('-weight')
        p_list = [ap.associated_product for ap in associated_products]
        context = {
            'product': product,
            'associated_products': p_list,
        }
        print(context)
        return render(request, 'products/product_detail.html', context)

