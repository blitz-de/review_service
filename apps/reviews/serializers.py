from rest_framework import serializers
from .models import Rating, Rater, Reply

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = [
            'pkid',
            'rating',
            'comment',
            'rated_user'
        ]


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ('reply_content',)


class CustomReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('rating', 'comment')