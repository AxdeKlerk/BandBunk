from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('overall_rating', 'cleanliness_rating', 'noise_rating', 'hospitality_rating', 'body')
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell others about your experience...'}),
        }
        labels = {
            'overall_rating':     'Overall ★',
            'cleanliness_rating': 'Cleanliness ★',
            'noise_rating':       'Noise / Respect ★',
            'hospitality_rating': 'Hospitality ★',
        }
