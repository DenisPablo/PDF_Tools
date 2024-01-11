from django.urls import path
from . import views

urlpatterns = [
    path('join_pdfs', views.join_PDF, name='join_PDFs')
]