from django.contrib import admin
from .models import Listing, ListingPhoto


class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    extra = 1


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'host', 'listing_type', 'town_city', 'price_per_night', 'is_active', 'created_at')
    list_filter = ('listing_type', 'is_active', 'includes_breakfast', 'allows_instruments')
    search_fields = ('title', 'town_city', 'postcode', 'host__username')
    list_editable = ('is_active',)
    inlines = [ListingPhotoInline]
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ListingPhoto)
class ListingPhotoAdmin(admin.ModelAdmin):
    list_display = ('listing', 'caption', 'is_primary', 'order')
