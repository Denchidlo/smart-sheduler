from django.urls import path
from .views import BotResponcer
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', csrf_exempt(BotResponcer.as_view()), name='update'),
]
