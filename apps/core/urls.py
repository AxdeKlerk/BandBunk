from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('',              views.home_view,         name='home'),
    path('about/',        views.about_view,        name='about'),
    path('how-it-works/', views.how_it_works_view, name='how_it_works'),
    path('safety/',       views.safety_view,       name='safety'),
    path('contact/',      views.contact_view,      name='contact'),
    path('privacy/',      views.privacy_view,      name='privacy'),
    path('terms/',        views.terms_view,        name='terms'),
]
