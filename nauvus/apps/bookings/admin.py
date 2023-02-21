from django.contrib import admin

from nauvus.apps.bookings.models import (
    BookLoad,
    BookLoadDeliveryProof,
    BookLoadLiveShare,
    BookLoadNotes,
    ExternalLoad,
    FavouriteLoad,
    LoadItem,
)


# Register your models here.
@admin.register(LoadItem)
class LoadItemAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "external_load_id",
    ]


@admin.register(BookLoad)
class BookLoadAdmin(admin.ModelAdmin):

    list_display = ["id", "load", "carrier", "driver", "status"]


@admin.register(BookLoadDeliveryProof)
class BookLoadDeliveryProofAdmin(admin.ModelAdmin):

    list_display = [
        "book_load",
        "proof",
    ]


@admin.register(FavouriteLoad)
class FavouriteLoadAdmin(admin.ModelAdmin):

    list_display = [
        "external_load_id",
        "is_favourite",
        "user",
    ]


@admin.register(ExternalLoad)
class ExternalLoadAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "driver",
        "broker",
    ]


@admin.register(BookLoadLiveShare)
class BookLoadLiveShareAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "book_load",
        "uid",
        "expiration_date",
    ]


@admin.register(BookLoadNotes)
class BookLoadNotesAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "book_load",
        "uid",
        "description",
    ]
