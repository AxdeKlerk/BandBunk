from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('confirmed', 'Confirmed'),
        ('declined', 'Declined'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    artist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings_as_artist'
    )

    check_in = models.DateField()
    check_out = models.DateField()
    num_guests = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Artist gig verification
    venue_name = models.CharField(max_length=200, help_text="Venue you are playing at")
    venue_address = models.CharField(max_length=300)
    gig_date = models.DateField(help_text="Date of the gig")
    band_name = models.CharField(max_length=200)
    social_proof_url = models.URLField(help_text="Link to gig listing, event page, or social post")

    # Artist's message to host
    message_to_host = models.TextField(blank=True)

    # Host's response
    host_response = models.TextField(blank=True)
    host_responded_at = models.DateTimeField(null=True, blank=True)

    # Stripe
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    stripe_charge_id = models.CharField(max_length=200, blank=True)
    payment_status = models.CharField(max_length=50, default='unpaid')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.band_name} @ {self.listing.title} ({self.check_in} → {self.check_out})"

    @property
    def num_nights(self):
        return (self.check_out - self.check_in).days

    def can_be_reviewed_by(self, user):
        from apps.reviews.models import Review
        if self.status != 'completed':
            return False
        if user == self.artist:
            return not Review.objects.filter(booking=self, reviewer=user, review_type='host').exists()
        if user == self.listing.host:
            return not Review.objects.filter(booking=self, reviewer=user, review_type='artist').exists()
        return False

    def confirm(self):
        self.status = 'confirmed'
        self.save()

    def decline(self):
        self.status = 'declined'
        self.host_responded_at = timezone.now()
        self.save()

    def complete(self):
        self.status = 'completed'
        self.save()
