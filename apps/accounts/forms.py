from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(
        choices=[
            ('host', 'Fan / Host — I have a sofa to offer'),
            ('artist', 'Artist / Band — I need somewhere to crash'),
            ('both', 'Both'),
        ],
        widget=forms.RadioSelect
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'user_type', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    pass


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'bio', 'profile_photo',
            'location', 'phone', 'user_type',
            'facebook_url', 'instagram_url', 'youtube_url',
            'bandcamp_url', 'spotify_url',
        )
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned = super().clean()
        user_type = cleaned.get('user_type')
        if user_type in ('artist', 'both'):
            has_social = any([
                cleaned.get('facebook_url'),
                cleaned.get('instagram_url'),
                cleaned.get('youtube_url'),
                cleaned.get('bandcamp_url'),
                cleaned.get('spotify_url'),
            ])
            if not has_social:
                raise forms.ValidationError(
                    "Artists must provide at least one social media or music platform link so hosts can verify you are a real band."
                )
        return cleaned
