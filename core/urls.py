from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView 
urlpatterns = [
    path('', include('listings.urls')),
    path('manifest.json', TemplateView.as_view(
        template_name='manifest.json', 
        content_type='application/json'
    ), name='manifest.json'),
    path('sw.js', TemplateView.as_view(
        template_name='sw.js', 
        content_type='application/javascript'
    ), name='sw.js'),
]