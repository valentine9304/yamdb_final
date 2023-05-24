from django.urls import path, include
from rest_framework.routers import DefaultRouter


from .views import (
    CategoryViewSet,
    GenreViewSet,
    SignUpViewSet,
    TitleViewSet,
    TokenViewSet,
    UserViewSet,
)
from api.views import ReviewViewSet, CommentViewSet

app_name = "api"

router = DefaultRouter()
router.register("users", UserViewSet)
router.register("categories", CategoryViewSet, basename="category")
router.register("genres", GenreViewSet, basename="genre")
router.register("titles", TitleViewSet, basename="title")
router.register(r"titles/(?P<title_id>\d+)/reviews",
                ReviewViewSet, basename="reviews")
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)


urlpatterns = [
    path("v1/auth/signup/", SignUpViewSet.as_view({"post": "create"}),
         name="signup"),
    path("v1/auth/token/", TokenViewSet.as_view({"post": "create"}),
         name="token"),
    path("v1/", include(router.urls)),
]
