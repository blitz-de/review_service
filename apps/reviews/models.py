import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import TimeStampedUUIDModel
# creating a pseudo primary key to get rid of the disavantages of UUID's


class UserProfile(models.Model):

    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.CharField(max_length=50, verbose_name=_("Profile's id"))
    username = models.CharField(max_length=20, verbose_name=_("User's username"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # both the rater and opponent are unique
        unique_together = ["id", "username"]

    def __str__(self):
        return self.username


class Rating(TimeStampedUUIDModel):
    class Range(models.IntegerChoices):
        RATING_1 = 1, _("Poor")
        RATING_2 = 2, _("Fair")
        RATING_3 = 3, _("Good")
        RATING_4 = 4, _("Very Good")
        RATING_5 = 5, _("Excellent")

    # it should trust the system that there is a user with a given user profile id
    # the person getting rated
    id = models.CharField(max_length=100,
        verbose_name=_("User providing the rating")
    )
    # the rater
    username = models.CharField(max_length=20,
                                      verbose_name="Opponent being rated"
    )
    # opponent = models.ForeignKey(
    #     opponents_id = UserProfile,
    #     verbose_name=_("Opponent being rated"),
    #     #related_name: otherwise, reverse query name for 'ratings.Rating.agent' clashes with field name 'profiles.Profile.rating'.
    #     related_name="opponent_review",
    #     on_delete=models.SET_NULL,
    #     null=True,
    # )
    rating = models.IntegerField(
        verbose_name=_("Rating"),
        choices=Range.choices,
        help_text="1=Poor, 2=Fair, 3=Good, 4=Very Good, 5=Excellent",
        default=0,
    )

    comment = models.TextField(verbose_name=_("Comment"))

    class Meta:
        # both the rater and opponent are unique
        unique_together = ["id", "username"]

    def __str__(self):
        return f"{self.id} rated at {self.username}"
