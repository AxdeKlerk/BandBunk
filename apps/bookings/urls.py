from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('',                              views.my_bookings_view,     name='my_bookings'),
    path('<int:pk>/',                     views.booking_detail_view,  name='detail'),
    path('request/<int:listing_pk>/',     views.request_booking_view, name='request'),
    path('<int:pk>/respond/',             views.host_respond_view,    name='respond'),
    path('<int:pk>/cancel/',              views.cancel_booking_view,  name='cancel'),
    path('<int:pk>/complete/',            views.mark_complete_view,   name='complete'),

    # Stripe
    path('<int:pk>/pay/',                 views.create_checkout_session_view, name='pay'),
    path('payment/success/',              views.payment_success_view,         name='payment_success'),
    path('<int:pk>/payment/cancelled/',   views.payment_cancelled_view,       name='payment_cancelled'),
    path('webhook/stripe/',               views.stripe_webhook_view,          name='stripe_webhook'),
]
