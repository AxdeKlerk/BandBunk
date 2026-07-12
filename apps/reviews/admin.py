from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'reviewer', 'reviewed_user', 'review_type',
        'overall_rating', 'is_public', 'created_at'
    )
    list_filter = ('review_type', 'overall_rating', 'is_public')
    search_fields = ('reviewer__username', 'reviewed_user__username', 'body')
    list_editable = ('is_public',)
    readonly_fields = ('created_at',)
