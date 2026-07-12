from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'band_name', 'listing', 'artist', 'check_in', 'check_out',
        'num_nights', 'total_price', 'status', 'payment_status', 'created_at'
    )
    list_filter = ('status', 'payment_status', 'gig_date')
    search_fields = ('band_name', 'venue_name', 'artist__username', 'listing__title')
    readonly_fields = ('created_at', 'updated_at', 'stripe_payment_intent_id', 'stripe_charge_id')
    actions = ['mark_completed', 'mark_confirmed', 'mark_cancelled']

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_completed.short_description = "Mark selected bookings as Completed"

    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_confirmed.short_description = "Mark selected bookings as Confirmed"

    def mark_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_cancelled.short_description = "Mark selected bookings as Cancelled"
