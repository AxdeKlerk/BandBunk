from django import forms
from django.utils import timezone
from .models import Booking


class BookingRequestForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = (
            'check_in', 'check_out', 'num_guests',
            'band_name', 'venue_name', 'venue_address',
            'gig_date', 'social_proof_url', 'message_to_host',
        )
        widgets = {
            'check_in':       forms.DateInput(attrs={'type': 'date'}),
            'check_out':      forms.DateInput(attrs={'type': 'date'}),
            'gig_date':       forms.DateInput(attrs={'type': 'date'}),
            'message_to_host': forms.Textarea(attrs={'rows': 4}),
            'venue_address':   forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'social_proof_url': 'Gig / event link (Facebook event, Eventbrite, Instagram post, etc.)',
        }

    def clean(self):
        cleaned = super().clean()
        check_in  = cleaned.get('check_in')
        check_out = cleaned.get('check_out')
        if check_in and check_out:
            if check_out <= check_in:
                raise forms.ValidationError("Check-out must be after check-in.")
            if check_in < timezone.now().date():
                raise forms.ValidationError("Check-in cannot be in the past.")
        return cleaned


class HostResponseForm(forms.ModelForm):
    class Meta:
        model  = Booking
        fields = ('host_response',)
        widgets = {'host_response': forms.Textarea(attrs={'rows': 3})}
