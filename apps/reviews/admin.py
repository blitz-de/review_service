from django.contrib import admin
from .models import Rating, Rater, Reply

class RaterAdmin(admin.ModelAdmin):

    list_display = ["id", "username", "nr_rated_users", 'is_admin', "is_signed"]


class RatingAdmin(admin.ModelAdmin):
    list_display = ['pkid', "rater", "rated_user"]


class ReplyAdmin(admin.ModelAdmin):
    list_display = ["reply_user", "replied_rating"]

admin.site.register(Rater, RaterAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Reply, ReplyAdmin)
