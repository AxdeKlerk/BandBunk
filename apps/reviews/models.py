from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    REVIEW_TYPE_CHOICES = [
        ('host', 'Review of Host / Listing'),
        ('artist', 'Review of Artist / Band'),
    ]

    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    booking = models.ForeignKey(
        'bookings.Booking',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    reviewed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received'
    )
    review_type = models.CharField(max_length=10, choices=REVIEW_TYPE_CHOICES)

    # Star ratings
    overall_rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    cleanliness_rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    noise_rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="For artists: how respectful of noise rules. For hosts: how quiet/comfortable."
    )
    hospitality_rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True,
        help_text="For artists: band behaviour. For hosts: warmth of welcome."
    )

    body = models.TextField(help_text="Tell others about your experience")
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('booking', 'reviewer', 'review_type')

    def __str__(self):
        return f"{self.reviewer.username} → {self.reviewed_user.username} ({self.review_type}, {self.overall_rating}★)"

    def stars_range(self):
        return range(self.overall_rating)

    def empty_stars_range(self):
        return range(5 - self.overall_rating)
