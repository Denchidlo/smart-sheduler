from django.urls import path  # pragma: no cover
from .views import BotResponcer  # pragma: no cover
from django.conf import settings  # pragma: no cover
from django.views.decorators.csrf import csrf_exempt  # pragma: no cover

urlpatterns = [  # pragma: no cover
    path("", csrf_exempt(BotResponcer.as_view()), name="update"),
]
