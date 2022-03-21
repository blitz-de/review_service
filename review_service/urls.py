from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("reviews/api/v1/ratings/", include("apps.reviews.urls")),
]
