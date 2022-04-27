from django.urls import path

from . import views

urlpatterns = [

    # GET
    # path("all/", views.RatingListAPIView.as_view(),
    #      name="all-reviews"),w
    path("users-ratings/<str:o_username>/", views.UserRatingsView.as_view(),#done
         name="users_ratings"),

    path("rated-user/<str:username>/", views.UserRatedView.as_view(),#done
         name="users_ratings"),

    path("ratings/<str:pk>/", views.RatingDetailsView.as_view(),#done
         name="rating_details"),
    path("my-reviews/<str:username>/", views.MyReviewsAPIView.as_view(),#done - fix to return my reviews
         name="my_reviews"),
    # POST
    path("rate/<str:rater_username>/", views.create_opponent_review, #done
         name="create-rating"),
    path("reply-to-review/<str:pk>/<str:username>/<str:o_username>/", views.ReplyToReviewAPIView.as_view(),
         name="reply_to_review"),
    # UPDATE
    path("update-review/<str:pk>/<str:username>/", views.UpdateReviewAPIView.as_view(),
         name="update_review"),
    # DELETE
    path("delete-review/<str:pk>/<str:username>/", views.DestroyReviewAPIView.as_view(),
         name="delete_review"),


]

## coverage html --> inside container ali rated Fadi8