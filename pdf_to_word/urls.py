from django.urls import path
from . import views

urlpatterns = [
    path('pdf_to_word', views.pdf_to_word, name='pdf_to_word')
]