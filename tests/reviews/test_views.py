from re import search

import pika

from apps.reviews.models import Rater, Rating, Reply
from apps.reviews.serializers import ReviewSerializer
import json
from rest_framework import status
from django.test import TestCase, Client
from django.urls import reverse
from django.db.models import Q



# initialize the APIClient app
from review_service.settings.base import env

client = Client()

class GetSingleRatingTest(TestCase):
    """ Test module for GET Rating Details API """

    def setUp(self):
        self.rating = Rating.objects.create(
            rating=2, comment='comment')

    def test_get_valid_single_user(self):
        response = client.get(
            reverse('rating_details', kwargs={'pk': self.rating.pk}))
        user = Rating.objects.get(pk=self.rating.pk)
        serializer = ReviewSerializer(user)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    #def test_get_invalid_single_user(self):
    #    response = client.get(
    #        reverse('rating_details', kwargs={'pk': 10}))
    #    self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class UserRatingsTest(TestCase):
    """ Test module for GET User Ratings API """

    def setUp(self):
        self.new_rater = Rater.objects.create(
            username='username1011')

        self.rating = Rating.objects.create(
            rating=2, comment='comment', rater=self.new_rater)

    def test_all_user_ratings(self):
        response = client.get(
            reverse('users_ratings', kwargs={'o_username': self.new_rater.username}))

        user_ratings = Rating.objects.filter(Q(rater=self.new_rater)).exists()
        if Rater.objects.filter(username=self.new_rater.username).exists():
            if user_ratings:
                ratings = Rating.objects.filter(Q(rater=self.new_rater))
                serializer = ReviewSerializer(ratings, many=True)
                resp = {
                    "users": serializer.data
                }
                self.assertEqual(response.data, resp)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertEqual(response.status_code, 403)

    def test_all_user_ratings_rater_dont_exist(self):
        response = client.get(
            reverse('users_ratings', kwargs={'o_username': 'non_user'}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # def rater_dont_exit(self):
    #     response = client.get(
    #         reverse('users_ratings', kwargs={'o_username': 'non_user'}))
    #     rater = {
    #         "username": "non_user",
    #     }
    #     if Rater.objects.filter(username=rater).exists():
    #         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class DestroyReviewTest(TestCase):
    """ Test module for Destroy Review API """

    def setUp(self):
        self.new_rater = Rater.objects.create(
            username='username1011', is_admin=True)

        self.rating = Rating.objects.create(
            rating=2, comment='comment', rater=self.new_rater, rated_user=self.new_rater)

    def test_destroy_user(self):
        response = self.client.delete(
            reverse('delete_review',
                    kwargs={'pk': int(self.rating.pk),
                            'username': self.new_rater.username}),
            content_type='application/json',
            follow=True
        )

        if Rating.objects.filter(Q(rater=self.new_rater)).exists():
            if Rating.objects.filter(Q(rater=self.new_rater))[0].is_admin or Rating.objects.filter(Q(rater=self.new_rater))[0].is_signed:
                reviews = self.new_rater.opponent_review.all()
                self.new_rater.nr_rated_users = reviews.count()
                total = 0

                for i in reviews:
                    total += i.rating
                if reviews.count() - 1 > 0:
                    self.new_rater.rating = round((total - self.rating / (reviews.count() - 1), 2))
                else:
                    self.new_rater.rating = 0
                    # self.new_rater.save()
                self.assertEqual(response.status_code, status.HTTP_200_OK)
            else:
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        else:
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_destroy_user_dont_exist(self):
        response = self.client.delete(
            reverse('delete_review',
                    kwargs={'pk': 10,
                            'username': self.new_rater.username}),
            content_type='application/json',
            follow=True
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class MyReviewsTest(TestCase):
    """ Test module for GET My Reviews API """

    def setUp(self):
        self.new_rater = Rater.objects.create(
            username='username1011', is_signed=True)

        self.rating = Rating.objects.create(
            rating=2, comment='comment', rater=self.new_rater)

    def test_all_user_ratings(self):
        response = client.get(
            reverse('my_reviews', kwargs={'username': self.new_rater.username}))

        user_ratings = Rating.objects.filter(Q(rater=self.new_rater)).exists()
        if Rater.objects.filter(username=self.new_rater.username).exists():
            if Rater.objects.filter(username=self.new_rater.username)[0].is_signed:
                if user_ratings:
                    ratings = Rating.objects.filter(Q(rater=self.new_rater))
                    serializer = ReviewSerializer(ratings, many=True)
                    self.assertEqual(response.status_code, status.HTTP_200_OK)
            else:
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        else:
            self.assertEqual(response.status_code, 403)

class UpdateReviewTest(TestCase):
    def setUp(self):
        self.new_rater = Rater.objects.create(
            username='username1011', is_signed=True)

        self.rated_user = Rater.objects.create(
            username='username101', is_signed=True)

        self.rating = Rating.objects.create(
            rating=2, comment='comment', rater=self.new_rater, rated_user=self.rated_user)

        self.rating_content={
            'rating':1,
            'comment':'great',
        }

    def test_update_review(self, request=None):
        response = self.client.put(
            reverse('update_review', kwargs={'pk': int(self.rating.pk), 'username': self.new_rater.username}),
            data=json.dumps(self.rating_content),
            content_type='application/json',
        )
        if Rater.objects.filter(username=self.new_rater.username)[0].is_signed:
            if self.new_rater.pk == self.rating.rater.pk:
                self.assertEqual(response.status_code, 201)
                self.rating.refresh_from_db()

        self.assertEqual(self.rating.comment, self.rating.comment)



class ReplyReviewTest(TestCase):
    def setUp(self):
        self.new_rater = Rater.objects.create(
            username='username1011', is_signed=True)

        self.rating = Rating.objects.create(
            rating=2, comment='comment', rater=self.new_rater)

        self.reply_content = {
            'reply_user':self.new_rater.pk,
            'replied_rating':self.rating.pk,
            'reply_content':'Great',
        }

    def test_reply_review(self):
        num_replies = Reply.objects.filter(reply_user__pk=self.rating.rater.pk).count()
        self.rating.num_replies = num_replies
        self.rating.save()
        response = self.client.post(
            reverse('reply_to_review',
                    kwargs={'pk': int(self.rating.pk),
                            'username': self.new_rater.username,
                            'o_username': self.rating.rater.username}),
            data=json.dumps(self.reply_content),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.rating.refresh_from_db()

# class RabbitMQTestCase(TestCase):
#
#     def connect_queue(self):
#         """
#         Create a connection to RabbitMQ server
#         @return: connection, channel
#         """
#         connection = pika.BlockingConnection(pika.URLParameters(env("RABBITMQ_HOST")))
#         channel = connection.channel()
#         return connection, channel
#
#         self.server = server
#
#
#     print("Server started waiting for Messages ")
#
#
#     def test_connect_queue(self):
#             self.assertTrue(env('RABBIT_HOST'))
#             response = self.connect_queue()
#             self.assertTrue(response)