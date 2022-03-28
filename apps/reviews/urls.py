from django.urls import path

from . import views

urlpatterns = [
    path("<str:rater_username>/", views.create_opponent_review,
         name="create-rating"),
    path("all/", views.RatingListAPIView.as_view(),
         name="all-reviews"),
]