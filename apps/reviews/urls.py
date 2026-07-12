from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('leave/<int:booking_pk>/<str:review_type>/', views.leave_review_view, name='leave'),
]
