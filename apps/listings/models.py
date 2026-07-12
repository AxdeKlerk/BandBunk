from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone


class Listing(models.Model):
    LISTING_TYPE_CHOICES = [
        ('sofa', 'Sofa'),
        ('spare_room', 'Spare Room'),
        ('floor_space', 'Floor Space / Blow-up Bed'),
        ('garage', 'Garage / Rehearsal Space'),
    ]

    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings'
    )
    title = models.CharField(max_length=200)
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPE_CHOICES)
    description = models.TextField()
    address_line1 = models.CharField(max_length=200)
    address_line2 = models.CharField(max_length=200, blank=True)
    town_city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    price_per_night = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=10.00,
        validators=[MinValueValidator(10.00)]
    )
    max_guests = models.PositiveIntegerField(default=1)
    max_nights = models.PositiveIntegerField(default=7, help_text="Maximum consecutive nights")

    # Amenities / what's included
    includes_breakfast = models.BooleanField(default=True, help_text="Tea/coffee and toast minimum")
    has_wifi = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    allows_instruments = models.BooleanField(default=False)
    is_pet_friendly = models.BooleanField(default=False)
    has_shower = models.BooleanField(default=False)

    # House rules
    house_rules = models.TextField(blank=True)
    noise_curfew = models.TimeField(null=True, blank=True)

    # Availability
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} — {self.town_city} ({self.get_listing_type_display()})"

    def average_rating(self):
        from apps.reviews.models import Review
        reviews = Review.objects.filter(booking__listing=self, review_type='host')
        if not reviews.exists():
            return None
        return round(sum(r.overall_rating for r in reviews) / reviews.count(), 1)

    def review_count(self):
        from apps.reviews.models import Review
        return Review.objects.filter(booking__listing=self, review_type='host').count()

    def is_available(self, check_in, check_out):
        from apps.bookings.models import Booking
        overlapping = Booking.objects.filter(
            listing=self,
            status__in=('confirmed', 'pending'),
            check_in__lt=check_out,
            check_out__gt=check_in
        )
        return not overlapping.exists()

    def get_type_icon(self):
        icons = {
            'sofa': '🛋️',
            'spare_room': '🚪',
            'floor_space': '💨',
            'garage': '🎸',
        }
        return icons.get(self.listing_type, '🏠')


class ListingPhoto(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='listings/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return f"Photo for {self.listing.title}"
