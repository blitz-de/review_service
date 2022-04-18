import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class Rater(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_("Raters's id"))
    username = models.CharField(primary_key=True, max_length=20, verbose_name=_("User's username"))
    nr_rated_users = models.IntegerField(
        verbose_name=_("Number of Reviews"), default=0, null=True, blank=True
    )
    is_signed = models.BooleanField(verbose_name=_("User Signed"),
                                    default=False)
    is_admin = models.BooleanField(verbose_name=_("User Admin"),
                                   default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Rating(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Range(models.IntegerChoices):
        RATING_1 = 1, _("Poor")
        RATING_2 = 2, _("Fair")
        RATING_3 = 3, _("Good")
        RATING_4 = 4, _("Very Good")
        RATING_5 = 5, _("Excellent")

    rater = models.ForeignKey(Rater,
                              verbose_name=_("User providing the rating"),
                              on_delete=models.SET_NULL, null=True)
    # models.CharField(max_length=50, verbose_name=_("User providing the rating"),#  blank=True,#  null=True)

    rated_user = models.ForeignKey(Rater,
                                   max_length=50, verbose_name=_("User being rated"),
                                   related_name="opponent_review",
                                   on_delete=models.SET_NULL, null=True)

    rating = models.IntegerField(
        verbose_name=_("Rating"),
        choices=Range.choices,
        help_text="1=Poor, 2=Fair, 3=Good, 4=Very Good, 5=Excellent",
        default=0,
    )
    num_replies = models.IntegerField(
        verbose_name=_("Number of Replies"), default=0, null=True, blank=True
    )

    comment = models.TextField(verbose_name=_("Comment"))

    class Meta:
        # both the rater and opponent are unique -> represent a pk
        unique_together = ["rater", "rated_user"]

    def __str__(self):
        return f"{self.rater} rated at {self.rated_user}"


class Reply(models.Model):
    pkid = models.BigAutoField(primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    reply_user = models.ForeignKey(Rater,
                                   verbose_name=_("User providing the reply"),
                                   on_delete=models.SET_NULL, null=True)

    replied_rating = models.ForeignKey(Rating, on_delete=models.CASCADE,
                                       max_length=50, verbose_name=_("Review being replied"),
                                       related_name="review_reply")

    reply_content = models.TextField(verbose_name=_("Reply"))

    class Meta:
        # both the rater and opponent are unique -> represent a pk
        unique_together = ["reply_user", "replied_rating"]

