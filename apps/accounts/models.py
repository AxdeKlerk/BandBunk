from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator


class User(AbstractUser):
    """
    Custom user model. A user can be a HOST, an ARTIST, or both.
    Both roles can exist on the same account.
    """
    USER_TYPE_CHOICES = [
        ('host', 'Host / Fan'),
        ('artist', 'Artist / Band'),
        ('both', 'Host & Artist'),
    ]

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='host')
    bio = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, help_text="Your town/city")
    phone = models.CharField(max_length=20, blank=True)

    # Social verification for artists
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    bandcamp_url = models.URLField(blank=True)
    spotify_url = models.URLField(blank=True)

    # Verification
    is_verified_artist = models.BooleanField(default=False)
    date_joined_display = models.DateField(auto_now_add=True)

    def is_host(self):
        return self.user_type in ('host', 'both')

    def is_artist(self):
        return self.user_type in ('artist', 'both')

    def has_social_link(self):
        return any([
            self.facebook_url, self.instagram_url,
            self.youtube_url, self.bandcamp_url, self.spotify_url
        ])

    def average_rating_as_host(self):
        from apps.reviews.models import Review
        reviews = Review.objects.filter(reviewed_user=self, review_type='host')
        if not reviews.exists():
            return None
        return round(sum(r.overall_rating for r in reviews) / reviews.count(), 1)

    def average_rating_as_artist(self):
        from apps.reviews.models import Review
        reviews = Review.objects.filter(reviewed_user=self, review_type='artist')
        if not reviews.exists():
            return None
        return round(sum(r.overall_rating for r in reviews) / reviews.count(), 1)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
