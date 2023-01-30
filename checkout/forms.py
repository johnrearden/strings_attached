from django.forms import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = {'full_name', 'email', 'phone_number', 'country', 'postcode',
                  'town_or_city', 'street_address1', ' street_address2',
                  'county', 'date', }

    def __init__(self, *args, **kwargs):
        """ Add placeholders, remove labels and autofocus on full_name field"""
        super().__init__(*args, **kwargs)
        self.fields['full_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            placeholder = field.replace('_', ' ').title()
            if self.fields[field].required:
                placeholder += ' *'
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].widget.attrs['class'] = None
            self.fields[field].label = False