import requests
from rest_framework import permissions, status, viewsets, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import DestroyAPIView, ListAPIView, GenericAPIView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models import Q
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from rest_framework.views import APIView

from .models import Rater, Reply
from .models import Rating
from requests.structures import CaseInsensitiveDict
from .producer import RabbitMq
from .serializers import ReviewSerializer, ReplySerializer, CustomReviewSerializer
from .decorators import time_calculator
r = RabbitMq()

@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def create_opponent_review(request, rater_username): # profile_id is the url_param (the person i want to rate)
    # permission_classes = [permissions.IsAuthenticated]
    data = request.data
    rater_user = get_object_or_404(Rater, username=rater_username)# is_signed=True,
    rated_user = get_object_or_404(Rater, username=data['rated_user'])# id=rater_id

    if rater_user.is_signed == True:

        print("@@@@@@@@@@@@@@@@@@@@@: ")
        print("$$$$$$$$$$$$$$$$$ ", rated_user.username)
        # opponent = username
        print("$$$$$$$$$$$$$ ", data['rated_user'])

        # to check if raters are not rating themselves
        if rater_user.username == rated_user.username: # opponent_profile returns zizo (username)
            formatted_response = {"message": "You can't rate yourself"}
            return Response(formatted_response, status=status.HTTP_403_FORBIDDEN)

        # rated_user_username = str(rater_username)
        # print("R@@%@%@%@%@%@% rated_id: ", rated_user_username)

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
    if not rater_user.is_signed:
        print("You must sign in to be able to review another user")
        response = {
            "message": "Please sign in to rate",
            "status code": status.HTTP_403_FORBIDDEN
        }
        return Response(response, status=status.HTTP_403_FORBIDDEN)


# class RatingListAPIView(generics.ListAPIView):
#     # permission_classes = [permissions.IsAuthenticated]
#     print("I am here")
#     queryset = Rating.objects.all()
#     print("queryset: ", queryset)
#     serializer_class = ReviewSerializer(queryset, many=True)


#API for getting all the reviews for a user
class UserRatingsView(APIView):
    permission_classes = permission_classes = (AllowAny,)
    serializer_class = ReviewSerializer
    print("blub")
    def get_object(self, o_username):
        try:
            return get_object_or_404(Rater, username=o_username)
        except Rater.DoesNotExist:
            raise Http404


    def get(self, request, o_username):
        related_user = self.get_object(o_username)
        if Rating.objects.filter(rater=related_user).exists():
            reviews = Rating.objects.filter(rater=related_user)
            serializer = ReviewSerializer(reviews, many=True, context={"request": request})
            print(serializer.data)
        if not Rating.objects.filter(rater=related_user).exists():
            response = {
                "response": "{} doesn't have any reated user".format(o_username)
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.data, status=status.HTTP_200_OK)


#API for getting the details of review on <id>
class RatingDetailsView(APIView):
    permission_classes = permission_classes = (AllowAny,)
    serializer_class = ReviewSerializer

    def get_object(self, pk):
        try:
            return get_object_or_404(Rating, pk=pk)
        except Rater.DoesNotExist:
            raise Http404


    def get(self, request, pk):
        related_rating = self.get_object(pk)
        serializer = ReviewSerializer(related_rating, context={"request": request})
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


#API for deleting a review on <id>
class DestroyReviewAPIView(DestroyAPIView):
    #permission_classes = (permissions.IsAdminUser, permissions.IsAuthenticated)
    permission_classes = (permissions.AllowAny,)
    serializer_class = ReviewSerializer

    def get_object(self, pk, username):
        try:
            return get_object_or_404(Rating, pk=pk, rater__username=username)
        except Rating.DoesNotExist:
            raise Http404

    def get_rater(self, username):
        try:
            return get_object_or_404(Rater, username=username)
        except Rater.DoesNotExist:
            raise Http404

    def get(self, request, pk, username):
        related_rating = self.get_object(pk, username)
        serializer = ReviewSerializer(related_rating, context={"request": request})
        print(serializer.data)
        print(request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk, username):
        with transaction.atomic():
            instance = self.get_object(pk, username)
            rated_user = self.get_object(pk, username).rated_user
            reviews = self.get_rater(username).opponent_review.all()

            u_rater = self.get_rater(username)

            if u_rater.is_signed or u_rater.is_admin:
                if Rating.objects.filter(Q(rater=u_rater) & Q(pk=instance.pk)).exists():
                    print(rated_user)
                    print("reviews: ", reviews.count())

                    # using len would be a bad idea because len will slower down the deletion process.
                    rated_user.num_reviews = reviews.count() #len(reviews)

                    total = 0
                    for i in reviews:
                        total += i.rating

                    if reviews.count() - 1 > 0:
                        rated_user.rating = round((total - instance.rating / (reviews.count() - 1), 2))
                    else:
                        rated_user.rating = 0

                    rated_user.save()
                    print(rated_user.rating)

                    instance.delete()
                else:
                    transaction.set_rollback(True)
                    message = {"message": "You aren't authorized to delete this review"}
                    return Response(message, status=status.HTTP_403_FORBIDDEN)
            else:
                transaction.set_rollback(True)
                message = {"message": "You're not signed in!"}
                return Response(message, status=status.HTTP_403_FORBIDDEN)

        return Response({"detail": "Review deleted"}, status=status.HTTP_200_OK)


#API for updating review
class UpdateReviewAPIView(APIView):
    #permission_classes = (permissions.IsAdminUser, permissions.IsAuthenticated)
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomReviewSerializer

    def get_object(self, pk):
        try:
            return get_object_or_404(Rating, pk=pk)
        except Rating.DoesNotExist:
            raise Http404

    def get_rater(self, username):
        try:
            return get_object_or_404(Rater, username=username)
        except Rater.DoesNotExist:
            raise Http404

    def put(self, request, pk, username, format=None):
        with transaction.atomic():
            selected_details = self.get_object(pk)
            related_rater = self.get_rater(username)
            if related_rater.is_signed:
                if related_rater.pk == selected_details.rater.pk:
                    serializer = CustomReviewSerializer(selected_details, data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        response = {"updated review": serializer.data}
                        return Response(response, status = status.HTTP_201_CREATED)
                    else:
                        print("invalid form")
                        response = {"detail": "Invalid Form"}
                        return Response(response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    transaction.set_rollback(True)
                    message = {"message": "You aren't authorized to update this review"}
                    return Response(message, status=status.HTTP_403_FORBIDDEN)
            else:
                transaction.set_rollback(True)
                message = {"message": "You're not signed in!"}
                return Response(message, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#API to fetch my reviews
class MyReviewsAPIView(APIView):
    #permission_classes = (permissions.IsAdminUser, permissions.IsAuthenticated)
    permission_classes = (permissions.AllowAny,)
    serializer_class = ReviewSerializer

    def get_object(self, username):
        try:
            return get_object_or_404(Rater, username=username)
        except Rater.DoesNotExist:
            raise Http404


    def get(self, request, username):
        related_user = self.get_object(username)

        if related_user.is_signed:
            if Rating.objects.filter(rater=related_user).exists():
                reviews = Rating.objects.filter(rater=related_user)
                serializer = ReviewSerializer(reviews, many=True, context={"request": request})
                print(serializer.data)
            if not Rating.objects.filter(rater=related_user).exists():
                response = {"response": "{} doesn't have any reated user".format(username)}
                return Response(response, status=status.HTTP_404_NOT_FOUND)
        if not related_user.is_signed:
            response = {
                "message": "Please sign in to get your reviews",
                "status code": status.HTTP_403_FORBIDDEN
            }
            return Response(response, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.data, status=status.HTTP_200_OK)


#API to comment on my review
class ReplyToReviewAPIView(GenericAPIView):
    #permission_classes = (permissions.IsAdminUser, permissions.IsAuthenticated)
    permission_classes = (permissions.AllowAny,)
    serializer_class = ReplySerializer

    def get_object(self, pk, o_username):
        try:
            return get_object_or_404(Rating, pk=pk, rater__username=o_username)
        except Rating.DoesNotExist:
            raise Http404

    def get_rater(self, username):
        try:
            return get_object_or_404(Rater, username=username)
        except Rater.DoesNotExist:
            raise Http404

    def post(self, request, pk, username, o_username):
        with transaction.atomic():
            instance = self.get_object(pk, o_username)
            print(instance)
            u_rater = self.get_rater(username)
            print(u_rater)

            if u_rater.is_signed:
                if Rating.objects.filter(Q(pk=instance.pk)).exists():
                    # Create a serializer with request.data
                    #serializer = self.get_serializer(data=request.data)
                    #if serializer.is_valid(raise_exception=True):
                    #    serializer.save()
                    print(request.data)
                    reply_exists = Reply.objects.filter(reply_user=u_rater, replied_rating=instance).exists()
                    if not reply_exists:
                        Reply.objects.create(reply_user=u_rater, replied_rating=instance, reply_content=request.data.get('reply_content'))
                        num_replies = Reply.objects.filter(reply_user__pk=self.get_object(pk, o_username).pk).count()
                        instance.num_replies = num_replies
                        instance.save()
                    else:
                        response = {"detail": "Review already replied"}
                        return Response(response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    transaction.set_rollback(True)
                    message = {"message": "This review doesn't exist"}
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)
            else:
                transaction.set_rollback(True)
                message = {"message": "You're not signed in!"}
                return Response(message, status=status.HTTP_403_FORBIDDEN)

        return Response({"detail": "Replied"}, status=status.HTTP_200_OK)

