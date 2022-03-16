from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import UserProfile

from .models import Rating

User = get_user_model()


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def create_opponent_review(request, profile_id): # profile_id is the url_param (the person i want to rate)
    opponent_profile = UserProfile.objects.get(id=profile_id, is_opponent=True)
    data = request.data
    # Rating {pk: "", rating: "", comment: ""} ---> pk is consisted of username and id

    # opponent = username
    profile_user = UserProfile.objects.get(username=opponent_profile.username)
    # need to consume email too, or may not, just user username
    # if opponent.username == request.username
    if profile_user.email == request.user.email:
        formatted_response = {"message": "You can't rate yourself"}
        return Response(formatted_response, status=status.HTTP_403_FORBIDDEN)

    # consume review_id
    # alreadyExists = opponent_profile.review_id.filter(opponent__username=opponent_profile.username).exists()
    alreadyExists = opponent_profile.opponent_review.filter(
        opponent__pkid=profile_user.pkid
    ).exists()

    if alreadyExists:
        formatted_response = {"detail": "Profile already reviewed"}
        return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)

    elif data["rating"] == 0:
        formatted_response = {"detail": "Please select a rating"}
        return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)

    else:
        review = Rating.objects.create(
            rater=request.user,
            opponent=opponent_profile,
            rating=data["rating"],
            comment=data["comment"],
        )
        reviews = opponent_profile.opponent_review.all()
        opponent_profile.num_reviews = len(reviews)

        total = 0
        for i in reviews:
            total += i.rating

        opponent_profile.rating = round(total / len(reviews), 2)
        opponent_profile.save()
        return Response("Review Added")
