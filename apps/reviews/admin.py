from django.contrib import admin
from .models import Rating, Rater, RatedUser

class RaterAdmin(admin.ModelAdmin):

    list_display = ["id", "username", "nr_rated_users", "is_signed"]

class RatedUserAdmin(admin.ModelAdmin):

    list_display = ["id", "username", "num_reviews"]

admin.site.register(Rater, RaterAdmin)
admin.site.register(RatedUser, RatedUserAdmin)
admin.site.register(Rating)
# admin.site.register(Rater)
# admin.site.register(RatedUser)