from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('pf/<str:raid_slug>/', views.pf_page, name='pf_page'),
    path('api/pf/<str:raid_slug>/', views.pf_results, name='pf_results'),
]