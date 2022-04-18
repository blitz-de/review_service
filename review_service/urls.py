from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url

from rest_framework import permissions
from rest_framework_swagger.views import get_swagger_view


schema_view = get_swagger_view(title='Pastebin API')
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
    path("reviews/api/", include("apps.reviews.urls")),
    path('reviews/api/swagger/', schema_view),


    # path('reviews/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # path('reviews/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
