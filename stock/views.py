from django.views.generic.edit import FormView, UpdateView
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.db.models import F, Q
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from .forms import ProductAddForm
from products.models import Product, SpecialOffer
from itertools import chain
from datetime import datetime


class ProductAddView(UserPassesTestMixin, SuccessMessageMixin, FormView):
    """ A form to allow staff to add a new product """
    template_name = 'stock/product_add_form.html'
    form_class = ProductAddForm
    success_url = '/stock/staff_product_list/all'
    success_message = "%(name)s was added successfully"

    def form_valid(self, form):
        form.save()
        return super(ProductAddView, self).form_valid(form)

    def test_func(self):
        """
        User passes test mixin calls this function to ensure that the user
        has the correct permission to see the content on the page
        """
        return self.request.user.is_staff


class ProductUpdateView(UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """ A form to allow staff to update an existing product """
    model = Product
    template_name = 'stock/product_update_form.html'
    fields = ['name', 'category', 'description', 'price', 'image',
              'audio_clip', 'stock_level', 'reorder_threshold',
              'product_owner']
    success_url = '/stock/staff_product_list/all'
    success_message = "%(name)s was edited successfully"

    def form_valid(self, form):
        form.save()
        return super(ProductUpdateView, self).form_valid(form)

    def test_func(self):
        """
        User passes test mixin calls this function to ensure that the user
        has the correct permission to see the content on the page
        """
        return self.request.user.is_staff


class StaffProductList(UserPassesTestMixin, View):
    """
    Provides a table summarising the complete list of products, which can
    be filtered and sorted by name, category, price and
    stock-below-reorder-threshold. Because some prices can be reduced, the
    price sorting is implemented in python after accessing the database.
    """
    def get(self, request, sort_key):
        reverse = '' if sort_key[0] == '-' else '-'
        product_order = ''
        category_order = ''
        price_order = ''
        manager = Product.objects
        if 'all' in sort_key:
            product_list = manager.all().order_by(f'{reverse}name')
            product_order = '' if sort_key[0] == '-' else '-'
        elif 'stock-low' in sort_key:
            low_query = Q(stock_level__lte=F('reorder_threshold'))
            stock_low_list = manager.all().filter(low_query)
            normal_query = Q(stock_level__gt=F('reorder_threshold'))
            stock_normal_list = manager.all().filter(normal_query)
            product_list = list(chain(stock_low_list, stock_normal_list))
        elif sort_key == 'category':
            product_list = manager.all().order_by(f'{reverse}category')
            category_order = '' if sort_key[0] == '-' else '-'
        else:
            product_list = manager.all()

        # Check for special offers and adjust price accordingly.
        items = []
        now = datetime.now()
        queries = Q(start_date__lte=now) & Q(end_date__gte=now)
        for prod in product_list:
            offers = SpecialOffer.objects.filter(product=prod) \
                .filter(queries) \
                .order_by('reduced_price')
            on_offer = True if offers else False
            price = offers[0].reduced_price if on_offer else prod.price
            item = {
                'name': prod.name,
                'image': prod.image.url,
                'id': prod.id,
                'price': price,
                'category': prod.category.name,
                'stock': prod.stock_level,
                'threshold': prod.reorder_threshold,
                'stock_low': prod.stock_level < prod.reorder_threshold
                and prod.stock_level > 0,
                'out_of_stock': prod.stock_level == 0,
                'on_special': on_offer,
            }
            items.append(item)

            # If required, sort items on effective price (incl. special offers)
            if 'price' in sort_key:
                if sort_key[0] == '-':
                    items = sorted(items, key=lambda x: x['price'],
                                   reverse=True)
                else:
                    items = sorted(items, key=lambda x: x['price'])
                price_order = '' if sort_key[0] == '-' else '-'

        context = {
            'products': items,
            'product_order': product_order,
            'category_order': category_order,
            'price_order': price_order,
        }
        return render(request, 'stock/staff_product_list.html', context)

    def test_func(self):
        """
        User passes test mixin calls this function to ensure that the user
        has the correct permission to see the content on the page
        """
        return self.request.user.is_staff


class DeleteProduct(UserPassesTestMixin, View):
    """
    Deletes a product from the database permanently.
    """
    def post(self, request):
        product_id = request.POST.get('product-id')
        redirect_url = request.POST.get('redirect_url')
        product = get_object_or_404(Product, pk=product_id)
        msg = f'Removed "{product.name}" from the product list'
        messages.success(request, msg)
        product.delete()
        return redirect(redirect_url)

    def test_func(self):
        """
        User passes test mixin calls this function to ensure that the user
        has the correct permission to see the content on the page
        """
        return self.request.user.is_staff
