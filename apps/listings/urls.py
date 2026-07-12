from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('',             views.browse_view,       name='browse'),
    path('map/',         views.map_view,           name='map'),
    path('create/',      views.create_listing_view, name='create'),
    path('mine/',        views.my_listings_view,   name='my_listings'),
    path('<int:pk>/',    views.listing_detail_view, name='detail'),
    path('<int:pk>/edit/', views.edit_listing_view, name='edit'),
    path('<int:pk>/toggle/', views.toggle_listing_view, name='toggle'),
]
