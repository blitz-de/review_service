from django.urls import path

from . import views

urlpatterns = [
    path("<str:rater_username>/", views.create_opponent_review,
         name="create-rating"),
    # path("all/", views.RatingListAPIView.as_view(),
    #      name="all-reviews"),
    path("users-ratings/<str:o_username>/", views.UserRatingsView.as_view(),
         name="users_ratings"),
    path("ratings/<str:pk>/", views.RatingDetailsView.as_view(),
         name="rating_details"),
    path("delete-review/<str:pk>/<str:username>/", views.DestroyReviewAPIView.as_view(),
         name="delete_review"),
    path("update-review/<str:pk>/<str:username>/", views.UpdateReviewAPIView.as_view(),
         name="update_review"),
    path("my-reviews/<str:username>/", views.MyReviewsAPIView.as_view(),
         name="my_reviews"),
    path("reply-to-review/<str:pk>/<str:username>/<str:o_username>/", views.ReplyToReviewAPIView.as_view(),
         name="reply_to_review"),
]