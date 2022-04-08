from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

from rest_framework import permissions
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi

# schema_view = get_schema_view(
#     openapi.Info(
#         title="Review Service APIs",
#         default_version='v1',
#         description="Test description",
#         terms_of_service="https://www.tenniscompanion.com/policies/terms/",
#         contact=openapi.Contact(email="contact@companiono.local"),
#         license=openapi.License(name="BSD License"),
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )

urlpatterns = [
    path('admin/', admin.site.urls),
    path("reviews/api/v1/ratings/", include("apps.reviews.urls")),

    # path('reviews/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('reviews/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
