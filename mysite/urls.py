# mysite/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('board/', include('board.urls', namespace='board')),
    path('accounts/', include("accounts.urls", namespace='accounts')),
    
]       