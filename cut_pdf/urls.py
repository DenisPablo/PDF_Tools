from django.urls import path
from . import views

urlpatterns = [
    path('cut_pdf', views.cut_pdf, name='cut_pdf')
]