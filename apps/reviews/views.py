import requests
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Rater, RatedUser
from .models import Rating
from requests.structures import CaseInsensitiveDict
from .producer import RabbitMq

r = RabbitMq()

@api_view(["POST"])
# @permission_classes([permissions.IsAuthenticated])
@permission_classes([permissions.AllowAny])
def create_opponent_review(request, rater_username): # profile_id is the url_param (the person i want to rate)
    # permission_classes = [permissions.IsAuthenticated]

    # url = "http://userapp:8080/api/v1/profile/me/"
    # token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjQ4MDk0OTg5LCJqdGkiOiI3NzljZmUyMTBmMDc0MWFkODI4NjI2OGIwNjFkZjNiZSIsInVzZXJfaWQiOiI3MGY0OWI1NS0yNjFjLTRlNTQtYTI1ZS02YzRmNmYxZmRlZGYifQ.cs3HzlU2tBSnf6AlZMCGAy3jqkqsCQ2hqsdHEDWvkYI"
    # headers = CaseInsensitiveDict()
    # headers["Accept"] = "*/*"
    # headers["Authorization"] = f"Bearer {token}"
    #
    #
    # resp = requests.get(url, headers=headers)
    # print("@@@@@@@@@@@@@@@@@@@@@$%: ",
    #       resp)
    data = request.data

    print("@@@@@@@@@@@@@@@@@@@@@: ")
    rated_user = get_object_or_404(Rater, username=data['rated_user'])# id=rater_id
    print("$$$$$$$$$$$$$$$$$ ", rated_user.username)#
    # opponent = username
    print("$$$$$$$$$$$$$ ", data['rated_user'])
    # req = requests.get('http://localhost:8080/')
    rater_user = get_object_or_404(Rater, username=rater_username)# is_signed=True,
    print("$@$$$$$$$$$$$$$$$$$$$$ i am here")

    if rater_user.username == rated_user.username: # opponent_profile returns zizo (username)
        formatted_response = {"message": "You can't rate yourself"}
        return Response(formatted_response, status=status.HTTP_403_FORBIDDEN)
    rated_user_username = str(rater_username)
    print("R@@%@%@%@%@%@% rated_id: ", rated_user_username)

    reviewExists = Rating.objects.filter \
        (rater=rater_user,rated_user=rated_user).exists()
    if reviewExists:
        formatted_response = {"detail": "Profile already reviewed"}
        return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)
    elif data["rating"] == 0:
        formatted_response = {"detail": "Please select a rating"}
        return Response(formatted_response, status=status.HTTP_400_BAD_REQUEST)

    else:
        review = Rating.objects.create(
                # rater=request.user,
                rater=rater_user,
                rated_user=rated_user,
                rating=data["rating"],
                comment=data["comment"],
            )
        reviews = rated_user.opponent_review.all()
        print("reviews: ", reviews)
        rated_user.num_reviews = len(reviews)

        total = 0
        for i in reviews:
            total += i.rating

        rated_user.rating = round(total / len(reviews), 2)
        rated_user.save()

    RabbitMq.publish(r, "review_added", rated_user.username)
    # consume- > rated_user.reviews +=1
    print("^^^^^^^^^^^^^^^^^^^^^: Message published")
    return Response("Review Added", status=status.HTTP_201_CREATED)
