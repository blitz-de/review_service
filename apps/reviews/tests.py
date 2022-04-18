import json
from re import search

from django.db.models import Q
from django.test import TestCase, Client



# initialize the APIClient app
from django.urls import reverse
from rest_framework import status

from apps.reviews.models import Rating, Rater, Reply
from apps.reviews.serializers import ReviewSerializer

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

    def test_get_invalid_single_user(self):
        response = client.get(
            reverse('rating_details', kwargs={'pk': 1})) #10
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


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
                    "users" : serializer.data
                }
                self.assertEqual(response.data, resp)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        else:
            self.assertEqual(response.status_code, 403)


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
                self.new_rater.nr_rated_users = reviews.count() #len(reviews)
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

        self.rating = Rating.objects.create(
            rating=2, comment='comment', rater=self.new_rater)

        self.rating_content={
            'rating':12,
            'username':'great',
        }

    def test_update_review(self, request=None):
        response = self.client.put(
            reverse('update_review', kwargs={'pk': int(self.rating.pk), 'username': self.new_rater.username}),
            data=json.dumps(self.rating_content),
            content_type='application/json',
        )
        if Rater.objects.filter(username=self.new_rater.username)[0].is_signed:
            if self.new_rater.pk == self.rating.rater.pk:
                self.assertEqual(response.status_code, 400)
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

