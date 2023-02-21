import datetime

import pymongo
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import NotFound

from nauvus.api.serializers import BaseModelSerializer, BaseSerializer
from nauvus.apps.bookings.models import (
    BookLoad,
    BookLoadDeliveryProof,
    BookLoadLiveShare,
    ExternalLoad,
    FavouriteLoad,
    LoadItem,
)
from nauvus.apps.broker.api.serializers import BrokerSerializer
from nauvus.apps.broker.models import Broker, BrokerPlatForm
from nauvus.apps.carrier.models import (
    Carrier,
    CarrierBroker,
    CarrierDispatcher,
    CarrierUser,
)
from nauvus.apps.dispatcher.models import Dispatcher, DispatcherUser
from nauvus.apps.driver.models import CarrierDriver, Driver
from nauvus.auth.api.serializers import UserSerializer
from nauvus.users.models import User

# client = pymongo.MongoClient(settings.MONGODB_HOST)
# db = client[settings.MONOGO_DB_NAME]
# loads_col = db["loads_loads"]


class BookLoadCarrierSerializer(BaseModelSerializer):

    """Book the load for Carrier Organization"""

    owner = serializers.SerializerMethodField()

    class Meta:
        model = Carrier
        fields = (
            "id",
            "organization_name",
            "owner",
        )

    def get_owner(self, obj):
        try:
            carrier_user = CarrierUser.objects.get(carrier=obj, is_owner=True)
        except CarrierUser.DoesNotExist:
            raise NotFound("CarrierUser Not Found")
        try:
            user = User.objects.get(id=carrier_user.user.id)
            return UserSerializer(user).data
        except User.DoesNotExist:
            raise NotFound("User Not Found")


class BookLoadDriverSerializer(BaseModelSerializer):

    """Book Load For the Driver"""

    user = serializers.SerializerMethodField()

    class Meta:
        model = Driver
        fields = ("id", "user")

    def get_user(self, obj):
        return UserSerializer(obj.user).data


class DispatcherAdminInformationSerializer(BaseModelSerializer):

    """Information about dispatcher admin"""

    user = serializers.SerializerMethodField()

    class Meta:
        model = Dispatcher
        fields = ("id", "organization_name", "user")

    def get_user(self, obj):
        try:
            dispatcher_user = DispatcherUser.objects.get(
                dispatcher=obj.id, is_owner=True
            )
        except Exception:
            raise NotFound("Dispatcher User Not Found.")
        return UserSerializer(dispatcher_user.user).data


class LoadItemSerializer(BaseModelSerializer):

    """All Book Loads Detail"""

    broker = serializers.SerializerMethodField()

    class Meta:
        model = LoadItem
        exclude = (
            "uid",
            "created_at",
            "updated_at",
            "received_at",
            "metadata",
        )

    def get_broker(self, obj):
        return BrokerSerializer(obj.broker).data


class BookLoadSerializer(BaseModelSerializer):

    """Book Load Response Serializer"""

    load = serializers.SerializerMethodField()
    carrier = serializers.SerializerMethodField()
    driver = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    dispatcher = serializers.SerializerMethodField()

    class Meta:
        model = BookLoad
        fields = (
            "id",
            "load",
            "carrier",
            "driver",
            "status",
            "user",
            "dispatcher",
            "book_by",
            # "is_booked_by_dispatcher",
            "rate_confirmation_document",
            "final_price",
            "created_at",
        )

    def get_load(self, obj):
        return LoadItemSerializer(obj.load).data

    def get_carrier(self, obj):
        return BookLoadCarrierSerializer(obj.carrier).data

    def get_driver(self, obj):
        return BookLoadDriverSerializer(obj.driver).data

    def get_user(self, obj):
        return UserSerializer(obj.user).data

    def get_dispatcher(self, obj):
        if obj.dispatcher:
            return DispatcherAdminInformationSerializer(obj.dispatcher).data
        else:
            return None


class BookLoadCreateSerializer(BaseModelSerializer):

    """Booking the Load"""

    # TODO: Add validation fot banking details

    external_load_id = serializers.CharField(max_length=500, required=True)
    carrier = serializers.IntegerField(required=False)
    driver = serializers.IntegerField(required=False)

    class Meta:
        model = BookLoad
        fields = (
            "external_load_id",
            "carrier",
            "driver",
        )

    def validate(self, data):


        request = self.context.get("request")

        try:
            user = User.objects.get(id=request.user.id)
        except Exception:
            raise NotFound("User Not Found")

        if not user.stripe_customer_id:
            raise serializers.ValidationError("Banking details are missing, please go to banking page to complete it.")

        if (
            user.user_type == User.CARRIER_OWNER
            or user.user_type == User.CARRIER_OWNER_OPERATOR
        ):
            try:
                carrier_user = CarrierUser.objects.get(
                    user=user, is_current_organization=True
                )
                carrier = carrier_user.carrier
            except Exception:
                raise NotFound("CarrierUser Not Found")

        elif user.user_type == User.DRIVER:
            try:
                driver = Driver.objects.get(user=user)
            except Exception:
                raise NotFound("Driver Not Found")
            try:
                carrier_driver = CarrierDriver.objects.get(
                    driver=driver,
                    is_current_carrier=True,
                    can_manage_load=True,
                )
                carrier = carrier_driver.carrier
            except Exception:
                raise NotFound("CarrierDriver Not Found")

        else:
            carrier = data.get("carrier")
            try:
                carrier = Carrier.objects.get(user=user)
            except Exception:
                raise NotFound("Carrier Not Found")

        try:
            book_load = BookLoad.objects.get(
                load__external_load_id=data.get("external_load_id"),
                carrier=carrier,
            )
            if book_load:
                raise NotFound("load is already booked with provided carrier.")
        except BookLoad.DoesNotExist:
            return data

    def validate_driver(self, value):
        try:
            driver = Driver.objects.get(id=value)
        except Exception:
            raise NotFound("Driver Not Found")

        if not driver.user.stripe_customer_id:
            raise serializers.ValidationError("Driver's banking details are missing, please go to banking page to complete it.")

        request = self.context.get("request")

        if request.user.user_type == User.DISPATCHER:
            try:
                carrier_driver = CarrierDriver.objects.get(
                    driver=driver,
                    carrier=request.data.get("carrier"),
                    is_current_carrier=True,
                )
            except CarrierDriver.DoesNotExist:
                raise NotFound("CarrierDriver Not Found")
        elif (
            request.user.user_type == User.CARRIER_OWNER
            or request.user.user_type == User.CARRIER_OWNER_OPERATOR
        ):
            try:
                carrier = CarrierUser.objects.get(
                    user=request.user,
                    is_current_organization=True,
                )
            except CarrierUser.DoesNotExist:
                raise NotFound("CarrierUser Not Found")

            try:
                carrier_driver = CarrierDriver.objects.get(
                    carrier=carrier.carrier,
                    driver=driver,
                    is_current_carrier=True,
                )

            except CarrierDriver.DoesNotExist:
                raise NotFound("CarrierDriver Not Found")

        book_load_driver = BookLoad.objects.filter(
            driver=carrier_driver.driver, status=BookLoad.IN_PROGRESS
        ).first()
        if book_load_driver:
            raise NotFound("Driver is already assigned to another load.")
        return driver

    def create(self, validated_data):

        request = self.context.get("request")
        external_load_id = validated_data.get("external_load_id")
        # try:
        #     mongo_load = loads_col.find_one({"id": external_load_id})
        # except pymongo.errors.OperationFailure:
        #     raise NotFound("Load Not Found")

        mongo_load = loads_col.find_one({"id": external_load_id})
        if mongo_load:
            pass
        else:
            raise NotFound("Load not Found.")

        try:
            user = User.objects.get(id=request.user.id)
        except Exception:
            raise NotFound("User Not Found")

        # try:
        #     carrier_user = CarrierUser.objects.get(
        #         user=user, is_current_organization=True
        #     )
        # except Exception:
        #     raise NotFound("CarrierUser Not Found")

        if user.user_type == User.DISPATCHER:
            book_by = BookLoad.DISPATCHER
            try:
                dispatcher_user = DispatcherUser.objects.get(
                    user=user,
                    is_current_organization=True,
                    access_type=DispatcherUser.FULL_ADMIN,
                )
            except DispatcherUser.DoesNotExist:
                raise NotFound("DispatcherUser Not Found")

            try:
                carrier = Carrier.objects.get(id=validated_data.get("carrier"))
            except Carrier.DoesNotExist:
                raise NotFound("Carrier Not Found")

            try:
                dispatcher_carriers = CarrierDispatcher.objects.get(
                    carrier=carrier.id,
                    dispatcher=dispatcher_user.dispatcher.id,
                    active=True,
                )
            except CarrierDispatcher.DoesNotExist:
                raise NotFound("CarrierDispatcher Not Found")

            carrier = dispatcher_carriers.carrier
            driver = validated_data.get("driver")
            dispatcher = dispatcher_carriers.dispatcher

        elif user.user_type == User.DRIVER:
            try:
                driver = Driver.objects.get(user=user)
            except Exception:
                raise NotFound("Driver Not Found")

            try:
                carrier_driver = CarrierDriver.objects.get(
                    driver=driver,
                    is_owner_operator=True,
                    is_current_carrier=True,
                )
                carrier = carrier_driver.carrier
                driver = driver
                dispatcher = None
            except Exception:
                raise NotFound("Carrier Driver Not Found.")

            book_by = BookLoad.DRIVER
            book_load_driver = BookLoad.objects.filter(
                driver=driver, status=BookLoad.IN_PROGRESS
            ).first()

            if book_load_driver:
                raise NotFound("Driver is already assigned to another load.")
        elif (
            user.user_type == User.CARRIER_OWNER
            or user.user_type == User.CARRIER_OWNER_OPERATOR
        ):
            try:
                carrier_user = CarrierUser.objects.get(
                    user=user,
                    is_current_organization=True,
                    access_type=CarrierUser.FULL_ADMIN,
                )
                carrier = carrier_user.carrier
                dispatcher = None
            except Exception:
                raise NotFound("CarrierUser Not Found")

            book_by = BookLoad.CARRIER
            is_booked_by_dispatcher = False
            driver = validated_data.get("driver")

        try:
            print(mongo_load["source"], ">>>>>>>>>>>>>>>>>>>")
            CarrierBroker.objects.get(
                carrier=carrier, broker__name=mongo_load["source"]
            )
        except CarrierBroker.DoesNotExist:
            raise NotFound("You are not associate with this load's source")

        broker, _ = Broker.objects.get_or_create(
            external_broker_id=mongo_load["poster_id"],
            name=mongo_load["poster_name"],
            phone=mongo_load["poster_phone"],
            mc_number=mongo_load["poster_mcnumber"],
            dot_number=mongo_load["poster_dotnumber"],
            metadata=mongo_load["metadata"]["poster"],
        )

        broker_platform = BrokerPlatForm.objects.filter(
            name=mongo_load["source"]
        ).first()
        if broker_platform is not None:
            source = broker_platform
        else:
            source = None
        load_item, _ = LoadItem.objects.get_or_create(
            source=source,
            commodity=mongo_load["commodity"],
            external_load_id=external_load_id,
            age=mongo_load["age"],
            posted_date=mongo_load["posted_date"],
            received_at=mongo_load["created_at"],
            computed_miledge=mongo_load["computed_miledge"],
            miledge=mongo_load["mileage"],
            origin_city=mongo_load["origin_city"],
            origin_state=mongo_load["origin_state"],
            origin_country=mongo_load["origin_country"],
            origin_geolocation_latitude=mongo_load[
                "origin_geolocation_latitude"
            ],
            origin_geolocation_longitude=mongo_load[
                "origin_geolocation_longitude"
            ],
            origin_deadhead="",
            destination_city=mongo_load["destination_city"],
            destination_state=mongo_load["destination_state"],
            destination_country=mongo_load["destination_country"],
            destination_geolocation_latitude=mongo_load[
                "destination_geolocation_latitude"
            ],
            destination_geolocation_longitude=mongo_load[
                "destination_geolocation_longitude"
            ],
            equipment_type=mongo_load["equipment_type"],
            pickup_date=mongo_load["pickup_date"],
            # pickup_date_time=mongo_load["pickup_date_time"],
            pickup_date_time=datetime.datetime.strptime(
                mongo_load["pickup_date_time"], "%a, %d %b %Y %H:%M:%S %Z"
            ),
            # pickup_date_time_utc=mongo_load["pickup_date_time_utc"],
            pickup_date_time_utc=datetime.datetime.strptime(
                mongo_load["pickup_date_time_utc"], "%a, %d %b %Y %H:%M:%S %Z"
            ),
            amount=mongo_load["amount"],
            amount_type=mongo_load["amount_type"],
            load_size=mongo_load["load_size"],
            load_length=mongo_load["load_length"],
            load_weight=mongo_load["load_weight"],
            number_of_stops=mongo_load["number_of_stops"],
            team_driving=mongo_load["team_driving"],
            load_status=mongo_load["load_status"],
            is_ocfp=mongo_load["is_ocfp"],
            metadata=mongo_load["metadata"],
            broker=broker,
        )

        book_load, _ = BookLoad.objects.get_or_create(
            load=load_item,
            # carrier=carrier_user.carrier,
            carrier=carrier,
            driver=validated_data.get("driver"),
            user=user,
            dispatcher=dispatcher,
            book_by=book_by,
        )

        return book_load


class BookLoadDeliveryProofSerializer(BaseModelSerializer):

    """Delivery Proof For the booked load"""

    delivered_at = serializers.SerializerMethodField()

    class Meta:
        model = BookLoadDeliveryProof
        fields = ("id", "book_load", "proof", "signature", "delivered_at")

    def get_delivered_at(self, obj):
        return obj.created_at


class BookLoadDeliveryDetailsSerializer(BaseModelSerializer):

    """Delivery Details of Booked load"""

    proof = serializers.SerializerMethodField()
    driver = serializers.SerializerMethodField()
    load = serializers.SerializerMethodField()

    class Meta:
        model = BookLoad
        fields = (
            "id",
            "load",
            "proof",
            "driver",
        )

    def get_proof(self, obj):
        proof = BookLoadDeliveryProof.objects.filter(book_load=obj.id).last()
        if proof:
            return BookLoadDeliveryProofSerializer(proof).data
        return None

    def get_driver(self, obj):
        return BookLoadDriverSerializer(obj.driver).data

    def get_load(self, obj):
        return LoadItemSerializer(obj.load).data


class FavouriteLoadCreateSerializer(BaseModelSerializer):

    """Add the Favourite load for user's"""

    external_load_id = serializers.CharField(max_length=500, required=True)

    class Meta:
        model = FavouriteLoad
        fields = ("external_load_id",)

    def create(self, validated_data):

        request = self.context.get("request")

        external_load_id = validated_data.get("external_load_id")
        try:
            mongo_load = loads_col.find_one({"id": external_load_id})
        except pymongo.errors.OperationFailure:
            raise NotFound("Load Not Found")

        if not mongo_load:
            raise NotFound("Load Not Found")
        else:
            pass

        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            raise NotFound("User Not Found")
        # external_broker_id = mongo_load["poster_id"]
        favourite_load, _ = FavouriteLoad.objects.get_or_create(
            commodity=mongo_load["commodity"],
            external_load_id=external_load_id,
            age=mongo_load["age"],
            posted_date=mongo_load["posted_date"],
            received_at=mongo_load["created_at"],
            computed_miledge=mongo_load["computed_miledge"],
            miledge=mongo_load["mileage"],
            origin_city=mongo_load["origin_city"],
            origin_state=mongo_load["origin_state"],
            origin_country=mongo_load["origin_country"],
            origin_geolocation_latitude=mongo_load[
                "origin_geolocation_latitude"
            ],
            origin_geolocation_longitude=mongo_load[
                "origin_geolocation_longitude"
            ],
            origin_deadhead="",
            destination_city=mongo_load["destination_city"],
            destination_state=mongo_load["destination_state"],
            destination_country=mongo_load["destination_country"],
            destination_geolocation_latitude=mongo_load[
                "destination_geolocation_latitude"
            ],
            destination_geolocation_longitude=mongo_load[
                "destination_geolocation_longitude"
            ],
            equipment_type=mongo_load["equipment_type"],
            pickup_date=mongo_load["pickup_date"],
            pickup_date_time=mongo_load["pickup_date_time"],
            pickup_date_time_utc=mongo_load["pickup_date_time_utc"],
            amount=mongo_load["amount"],
            amount_type=mongo_load["amount_type"],
            load_size=mongo_load["load_size"],
            load_length=mongo_load["load_length"],
            load_weight=mongo_load["load_weight"],
            number_of_stops=mongo_load["number_of_stops"],
            team_driving=mongo_load["team_driving"],
            load_status=mongo_load["load_status"],
            is_ocfp=mongo_load["is_ocfp"],
            metadata=mongo_load["metadata"],
            is_favourite=True,
            user=user,
        )

        return favourite_load


class LoadItemStopDetailsSerializer(BaseModelSerializer):

    """Stop Details for loads"""

    class Meta:
        model = LoadItem
        fields = (
            "origin_city",
            "origin_state",
            "origin_country",
            "origin_geolocation_latitude",
            "origin_geolocation_longitude",
            "destination_city",
            "destination_state",
            "destination_country",
            "destination_geolocation_latitude",
            "destination_geolocation_longitude",
        )


class BookLoadStopDetailsSerializer(BaseModelSerializer):

    """Stop Details for loads"""

    load = serializers.SerializerMethodField()

    class Meta:
        model = BookLoad
        fields = ("load",)

    def get_load(self, obj):
        return LoadItemStopDetailsSerializer(obj.load).data


class FavouriteLoadSerializer(BaseModelSerializer):

    """Favourite Load Response Serializer"""

    class Meta:
        model = FavouriteLoad
        exclude = (
            "uid",
            "created_at",
            "updated_at",
            "received_at",
            "metadata",
            "user",
        )


class BookLoadReassignDriverSerializer(BaseModelSerializer):

    """Reassign Driver For the Booked Load"""

    driver = serializers.IntegerField(required=True)

    class Meta:
        model = BookLoad
        fields = ("driver",)

    def validate_driver(self, value):
        try:
            driver = Driver.objects.get(id=value)
        except Exception:
            raise NotFound("Driver Not Found")

        try:
            carrier_driver = CarrierDriver.objects.get(
                carrier=self.instance.carrier,
                driver=driver,
                is_current_carrier=True,
            )
        except Exception:
            raise NotFound("Carrier Driver Not Found")

        book_load_driver = (
            BookLoad.objects.filter(
                driver=carrier_driver.driver, status=BookLoad.IN_PROGRESS
            )
            .exclude(id=self.instance.id)
            .first()
        )
        if book_load_driver:
            raise NotFound("Driver is already assigned to another load.")
        return driver

    def update(self, instance, validated_data):

        instance.driver = validated_data.get("driver")
        instance.save()
        return instance


class ExternalLoadBookingSerializer(BaseModelSerializer):

    """Add External Loads"""

    class Meta:
        model = ExternalLoad
        fields = "__all__"

    def create(self, validated_data):

        request = self.context.get("request")

        try:
            if (
                request.user.user_type == User.DISPATCHER
                or request.user.user_type == User.CARRIER_OWNER
            ):
                driver = Driver.objects.get(id=request.data.get("driver"))
            elif request.user.user_type == User.DRIVER:
                driver = Driver.objects.get(user=request.user)
        except Exception:
            raise NotFound("Driver not Found")
        try:
            user = User.objects.get(id=request.user.id)
        except Exception:
            raise NotFound("User Not Found")

        if request.user.user_type == User.DISPATCHER:

            try:
                dispatcher = DispatcherUser.objects.get(
                    user=user,
                    is_current_organization=True,
                    access_type=DispatcherUser.FULL_ADMIN,
                )
            except DispatcherUser.DoesNotExist:
                raise NotFound("DispatcherUser Not Found")

            try:
                carrier = Carrier.objects.get(id=request.data.get("carrier"))
            except Carrier.DoesNotExist:
                raise NotFound("Carrier Not Found")

            try:
                dispatcher_carriers = CarrierDispatcher.objects.get(
                    carrier=carrier, dispatcher=dispatcher.dispatcher
                )
            except CarrierDispatcher.DoesNotExist:
                raise NotFound("CarrierDispatcher Not Found")

            carrier = dispatcher_carriers.carrier
            dispatcher = dispatcher_carriers.dispatcher

        elif request.user.user_type == User.DRIVER:
            try:
                carrier_driver = CarrierDriver.objects.get(
                    driver=driver,
                    can_manage_load=True,
                    is_current_carrier=True,
                )
            except Exception:
                raise NotFound("CarrierDriver Not Found")

            carrier = carrier_driver.carrier
            dispatcher = None
            is_booked_by_dispatcher = False

        elif (
            request.user.user_type == User.CARRIER_OWNER
            or request.user.user_type == User.CARRIER_OWNER_OPERATOR
        ):

            try:
                carrier_user = CarrierUser.objects.get(
                    user=user,
                    is_current_organization=True,
                    access_type=CarrierUser.FULL_ADMIN,
                )
                carrier = carrier_user.carrier
                dispatcher = None
            except Exception:
                raise NotFound("CarrierUser Not Found")

        book_load_driver = ExternalLoad.objects.filter(
            driver=driver, status=ExternalLoad.IN_PROGRESS
        ).first()
        if book_load_driver:
            raise NotFound("Driver is already assigned to another load.")

        try:
            carrier_broker = CarrierBroker.objects.get(
                id=request.data.get("broker"), carrier=carrier.id
            )
        except Exception:
            raise NotFound("Broker Not Found.")

        external_load = ExternalLoad.objects.create(
            rc_document=validated_data.get("rc_document"),
            customer_reference_number=validated_data.get(
                "customer_reference_number"
            ),
            pickup_address_city=validated_data.get("pickup_address_city"),
            pickup_address_state=validated_data.get("pickup_address_state"),
            pickup_address_zipcode=validated_data.get(
                "pickup_address_zipcode"
            ),
            dropoff_address_city=validated_data.get("dropoff_address_city"),
            dropoff_address_state=validated_data.get("dropoff_address_state"),
            dropoff_address_zipcode=validated_data.get(
                "dropoff_address_zipcode"
            ),
            pickup_contact_name=validated_data.get("pickup_contact_name"),
            pickup_phone_number=validated_data.get("pickup_phone_number"),
            pickup_email=validated_data.get("pickup_email"),
            pickup_number=validated_data.get("pickup_number"),
            pickup_additional_notes=validated_data.get(
                "pickup_additional_notes"
            ),
            dropoff_contact_name=validated_data.get("dropoff_contact_name"),
            dropoff_phone_number=validated_data.get("dropoff_phone_number"),
            dropoff_email=validated_data.get("dropoff_email"),
            dropoff_number=validated_data.get("dropoff_number"),
            dropoff_additional_notes=validated_data.get(
                "dropoff_additional_notes"
            ),
            pickup_date=validated_data.get("pickup_date"),
            dropoff_date=validated_data.get("dropoff_date"),
            weight=validated_data.get("weight"),
            load_price=validated_data.get("load_price"),
            broker=carrier_broker,
            driver=driver,
            carrier=carrier,
            dispatcher=dispatcher,
            packging_type=validated_data.get("packging_type"),
            equipment_type=validated_data.get("equipment_type"),
        )

        return external_load


class ExternalLoadInformationSerializer(BaseModelSerializer):

    """External Load Information Serializer"""

    class Meta:
        model = ExternalLoad
        fields = "__all__"


class ExternalLoadSerializer(BaseModelSerializer):

    """External Load Responser Serializer"""

    driver = serializers.SerializerMethodField()
    # rc_document = serializers.SerializerMethodField()
    pickup_address_city = serializers.SerializerMethodField()
    pickup_address_state = serializers.SerializerMethodField()
    pickup_address_zipcode = serializers.SerializerMethodField()
    dropoff_address_city = serializers.SerializerMethodField()
    dropoff_address_state = serializers.SerializerMethodField()
    dropoff_address_zipcode = serializers.SerializerMethodField()
    pickup_contact_name = serializers.SerializerMethodField()
    pickup_phone_number = serializers.SerializerMethodField()
    pickup_email = serializers.SerializerMethodField()
    pickup_number = serializers.SerializerMethodField()
    pickup_additional_notes = serializers.SerializerMethodField()
    dropoff_contact_name = serializers.SerializerMethodField()
    dropoff_phone_number = serializers.SerializerMethodField()
    dropoff_email = serializers.SerializerMethodField()
    dropoff_number = serializers.SerializerMethodField()
    dropoff_additional_notes = serializers.SerializerMethodField()
    pickup_date = serializers.SerializerMethodField()
    dropoff_date = serializers.SerializerMethodField()
    weight = serializers.SerializerMethodField()
    load_price = serializers.SerializerMethodField()
    broker = serializers.SerializerMethodField()
    carrier = serializers.SerializerMethodField()
    packging_type = serializers.SerializerMethodField()
    equipment_type = serializers.SerializerMethodField()

    class Meta:
        model = ExternalLoad
        fields = (
            "driver",
            # "rc_document",
            "pickup_address_city",
            "pickup_address_state",
            "pickup_address_zipcode",
            "dropoff_address_city",
            "dropoff_address_state",
            "dropoff_address_zipcode",
            "pickup_contact_name",
            "pickup_phone_number",
            "pickup_email",
            "pickup_number",
            "pickup_additional_notes",
            "dropoff_contact_name",
            "dropoff_phone_number",
            "dropoff_email",
            "dropoff_number",
            "dropoff_additional_notes",
            "pickup_date",
            "dropoff_date",
            "weight",
            "load_price",
            "broker",
            "carrier",
            "packging_type",
            "equipment_type",
        )

    def get_driver(self, obj):
        return obj.driver.id

    # def get_rc_document(self, obj):
    #     return obj.rc_document

    def get_pickup_address_city(self, obj):
        return obj.pickup_address_city

    def get_pickup_address_state(self, obj):
        return obj.pickup_address_state

    def get_pickup_address_zipcode(self, obj):
        return obj.pickup_address_zipcode

    def get_dropoff_address_city(self, obj):
        return obj.dropoff_address_city

    def get_dropoff_address_state(self, obj):
        return obj.dropoff_address_state

    def get_dropoff_address_zipcode(self, obj):
        return obj.dropoff_address_zipcode

    def get_pickup_contact_name(self, obj):
        return obj.pickup_contact_name

    def get_pickup_phone_number(self, obj):
        return obj.pickup_phone_number

    def get_pickup_email(self, obj):
        return obj.pickup_email

    def get_pickup_number(self, obj):
        return obj.pickup_number

    def get_pickup_additional_notes(self, obj):
        return obj.pickup_additional_notes

    def get_dropoff_contact_name(self, obj):
        return obj.dropoff_contact_name

    def get_dropoff_phone_number(self, obj):
        return obj.dropoff_phone_number

    def get_dropoff_email(self, obj):
        return obj.dropoff_email

    def get_dropoff_number(self, obj):
        return obj.dropoff_number

    def get_dropoff_additional_notes(self, obj):
        return obj.dropoff_additional_notes

    def get_pickup_date(self, obj):
        return obj.pickup_date

    def get_dropoff_date(self, obj):
        return obj.dropoff_date

    def get_weight(self, obj):
        return obj.weight

    def get_load_price(self, obj):
        return obj.load_price

    def get_broker(self, obj):
        return obj.broker.id

    def get_carrier(self, obj):
        return obj.carrier.id

    def get_packging_type(self, obj):
        return obj.packging_type

    def get_equipment_type(self, obj):
        return obj.equipment_type


class ExternalLoadUpdateSerializer(BaseModelSerializer):

    """Update the information of external load."""

    driver = serializers.IntegerField(required=True)
    carrier = serializers.IntegerField(required=True)
    broker = serializers.IntegerField(required=True)

    class Meta:
        model = ExternalLoad
        fields = "__all__"

    def validate_driver(self, value):
        try:
            driver = Driver.objects.get(id=value)
        except Exception:
            raise NotFound("Driver Not Found")

        book_load_driver = ExternalLoad.objects.filter(
            driver=driver, status=ExternalLoad.IN_PROGRESS
        ).first()

        if book_load_driver:
            raise NotFound("Driver is already assigned to another load.")

        return driver

    def validate_carrier(self, value):
        try:
            carrier = Carrier.objects.get(id=value)
        except Exception:
            raise NotFound("Driver Not Found")

        return carrier

    def validate_broker(self, value):
        request = self.context.get("request")
        try:
            carrier = CarrierUser.objects.get(user=request.user)
            broker = CarrierBroker.objects.filter(
                broker=value, carrier=carrier.carrier
            ).first()
        except Exception:
            raise NotFound("Broker Not Found.")

        return broker

    def update(self, instance, validated_data):

        instance.customer_reference_number = validated_data.get(
            "customer_reference_number"
        )
        instance.pickup_address_city = validated_data.get(
            "pickup_address_city"
        )
        instance.pickup_address_state = validated_data.get(
            "pickup_address_state"
        )
        instance.pickup_address_zipcode = validated_data.get(
            "pickup_address_zipcode"
        )
        instance.dropoff_address_city = validated_data.get(
            "dropoff_address_city"
        )
        instance.dropoff_address_state = validated_data.get(
            "dropoff_address_state"
        )
        instance.dropoff_address_zipcode = validated_data.get(
            "dropoff_address_zipcode"
        )
        instance.pickup_contact_name = validated_data.get(
            "pickup_contact_name"
        )
        instance.pickup_phone_number = validated_data.get(
            "pickup_phone_number"
        )
        instance.pickup_email = validated_data.get("pickup_email")
        instance.pickup_number = validated_data.get("pickup_number")
        instance.pickup_additional_notes = validated_data.get(
            "pickup_additional_notes"
        )
        instance.dropoff_contact_name = validated_data.get(
            "dropoff_contact_name"
        )
        instance.dropoff_phone_number = validated_data.get(
            "dropoff_phone_number"
        )
        instance.dropoff_email = validated_data.get("dropoff_email")
        instance.dropoff_number = validated_data.get("dropoff_number")
        instance.dropoff_additional_notes = validated_data.get(
            "dropoff_additional_notes"
        )
        instance.pickup_date = validated_data.get("pickup_date")
        instance.dropoff_date = validated_data.get("dropoff_date")
        instance.weight = validated_data.get("weight")
        instance.load_price = validated_data.get("load_price")
        instance.broker = validated_data.get("broker")
        instance.driver = validated_data.get("driver")
        instance.carrier = validated_data.get("carrier")
        instance.packging_type = validated_data.get("packging_type")
        instance.equipment_type = validated_data.get("equipment_type")

        instance.save()

        return instance


class LiveShareCreateSerializer(BaseModelSerializer):

    expiration_date = serializers.DateTimeField(required=True)

    class Meta:
        model = BookLoadLiveShare
        fields = ("expiration_date",)


class LiveShareRetrieveSerializer(BaseSerializer):

    uid = serializers.CharField(max_length=500, required=True)
