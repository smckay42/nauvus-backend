from rest_framework.routers import DefaultRouter

from nauvus.apps.bookings.api.views import BookLoadViewset, ExternalLoadBookingViewSet

app_name = "books"

router = DefaultRouter()

router.register(
    r"loads",
    BookLoadViewset,
    basename="book_loads",
)
# router.register(
#     r"favourites",
#     FavouriteLoadViewSet,
#     basename="favourite_loads",
# )

router.register(
    r"external-loads",
    ExternalLoadBookingViewSet,
    basename="external_loads",
)

urlpatterns = []
urlpatterns += router.urls
