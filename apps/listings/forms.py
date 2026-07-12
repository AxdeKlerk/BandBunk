from django import forms
from .models import Listing, ListingPhoto


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = (
            'title', 'listing_type', 'description',
            'address_line1', 'address_line2', 'town_city', 'postcode',
            'price_per_night', 'max_guests', 'max_nights',
            'includes_breakfast', 'has_wifi', 'has_parking',
            'allows_instruments', 'is_pet_friendly', 'has_shower',
            'house_rules', 'noise_curfew',
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'house_rules':  forms.Textarea(attrs={'rows': 3}),
            'noise_curfew': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean_price_per_night(self):
        price = self.cleaned_data['price_per_night']
        if price < 10:
            raise forms.ValidationError("Minimum price is £10 per night.")
        return price


class ListingPhotoForm(forms.ModelForm):
    class Meta:
        model  = ListingPhoto
        fields = ('image', 'caption', 'is_primary')


class ListingSearchForm(forms.Form):
    q        = forms.CharField(required=False, label='Town / City or Postcode')
    type     = forms.ChoiceField(
        required=False,
        choices=[('', 'All types')] + list(Listing.LISTING_TYPE_CHOICES)
    )
    max_price = forms.DecimalField(required=False, min_value=10, label='Max price per night')
    date      = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
