from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'is_verified_artist', 'date_joined')
    list_filter = ('user_type', 'is_verified_artist', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('BandBunk Profile', {
            'fields': (
                'user_type', 'bio', 'profile_photo', 'location', 'phone',
                'is_verified_artist',
            )
        }),
        ('Social Links', {
            'fields': (
                'facebook_url', 'instagram_url', 'youtube_url',
                'bandcamp_url', 'spotify_url',
            )
        }),
    )
    actions = ['verify_artists', 'unverify_artists']

    def verify_artists(self, request, queryset):
        queryset.update(is_verified_artist=True)
        self.message_user(request, f"{queryset.count()} artist(s) verified.")
    verify_artists.short_description = "✅ Verify selected artists"

    def unverify_artists(self, request, queryset):
        queryset.update(is_verified_artist=False)
        self.message_user(request, f"{queryset.count()} artist(s) unverified.")
    unverify_artists.short_description = "❌ Unverify selected artists"
