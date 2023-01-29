from django import forms
from products.models import Product


class ProductAddForm(forms.ModelForm):
    """ A form to allow staff members alter fields on a Product """
    class Meta:
        model = Product
        fields = ('name', 'category', 'description', 'price', 'image',
                  'audio_clip', 'stock_level', 'reorder_threshold',
                  'product_owner')
