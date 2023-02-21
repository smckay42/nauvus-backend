from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.db.models import Sum
from rest_framework import serializers

from nauvus.apps.broker.models import Broker
from nauvus.apps.carrier.models import Carrier
from nauvus.apps.dispatcher.api.serializers import DispatcherUserSerializer
from nauvus.apps.driver.models import Driver
from nauvus.apps.loads.models import DeliveryDocument, Load, LoadSource, validate_document_file
from nauvus.apps.payments.models import Invoice, LoadSettlement, Payment
from nauvus.base.validators import ZipCodeValidator
from nauvus.utils.location import Location

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        exclude = [
            "password",
            "stripe_customer_id",
            "password_reset_key",
            "is_superuser",
        ]


class LoadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoadSource
        fields = "__all__"


class BrokerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Broker
        fields = [
            "name",
            "email",
            "phone",
            "contact_first_name",
            "contact_last_name",
            "mc_number",
        ]


class LoadDriverSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Driver
        fields = "__all__"


class ContactSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    email = serializers.CharField(required=False, allow_blank=True, validators=[validate_email], allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if "phone" not in data and "email" not in data:
            raise serializers.ValidationError("A phone number or email address must be provided for contacts.")
        return data


class LocationSerializer(serializers.Serializer):
    city = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    zipcode = serializers.CharField(required=True, validators=[ZipCodeValidator])
    address1 = serializers.CharField(required=True)
    address2 = serializers.CharField(required=False)
    contact = ContactSerializer(required=True)

    def validate(self, data):
        city = data["city"]
        state = data["state"]
        try:
            coordinates = Location().get_city_coordinates(city, state)
            data["latitude"] = coordinates[0]
            data["longitude"] = coordinates[1]
        except AttributeError:
            raise serializers.ValidationError(f"City '{city}' and State '{state}' do not match.")

        return data


class LoadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Load
        fields = "__all__"

    def validate_final_rate(self, value):
        if value <= 0:
            raise serializers.ValidationError("Final rate must be greater than zero.")
        return value


class BookedLoadSerializer(LoadSerializer):

    pickup_date = serializers.DateTimeField(required=True)
    dropoff_date = serializers.DateTimeField(required=True)
    final_rate = serializers.DecimalField(required=True, decimal_places=2, max_digits=None)
    driver = serializers.IntegerField(required=True)
    origin = LocationSerializer()
    destination = LocationSerializer()
    contact = ContactSerializer(required=False)
    reference_title = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    invoice_email = serializers.CharField(
        required=True, allow_blank=False, allow_null=False, validators=[validate_email]
    )

    def validate(self, data):
        if data["pickup_date"] > data["dropoff_date"]:
            raise serializers.ValidationError("Pickup date must be on the same day or before the drop off date")

        if not self.instance.rc_document or self.instance.rc_document.name == "":
            raise serializers.ValidationError("Load must have a rate confirmation document before booking.")

        try:
            carrier = Carrier.objects.get(carrierdriver__driver=data["driver"])
            data["carrier"] = carrier
        except Exception:
            raise serializers.ValidationError("Unable to find a carrier associated with driver.")

        return data

    def validate_driver(self, value):
        try:
            driver = Driver.objects.get(pk=value)
            return driver
        except Driver.DoesNotExist:
            raise serializers.ValidationError(f"No driver found with id {value}")

    def update(self, instance: Load, validated_data):
        instance.current_status = Load.Status.BOOKED
        instance.invoice_email = validated_data.get("invoice_email", instance.invoice_email)
        instance.origin = validated_data.get("origin", instance.origin)
        instance.destination = validated_data.get("destination", instance.destination)
        instance.driver = validated_data.get("driver", instance.driver)
        instance.pickup_date = validated_data.get("pickup_date", instance.pickup_date)
        instance.dropoff_date = validated_data.get("dropoff_date", instance.dropoff_date)
        instance.details = validated_data.get("details", instance.details)
        instance.final_rate = validated_data.get("final_rate", instance.final_rate)
        instance.carrier = validated_data.get("carrier", instance.carrier)
        instance.save()
        return instance


class CreateLoadSerializer(LoadSerializer):
    broker = serializers.IntegerField(required=True)
    invoice_email = serializers.CharField(
        required=True, allow_blank=False, allow_null=False, validators=[validate_email]
    )
    final_rate = serializers.DecimalField(required=True, decimal_places=2, max_digits=None)
    rc_document = serializers.FileField(required=True, validators=[validate_document_file])

    def validate_broker(self, value):
        try:
            broker = Broker.objects.get(pk=value)
            return broker
        except Broker.DoesNotExist:
            raise serializers.ValidationError(f"No broker found with id {value}")

    def create(self, validated_data):
        # TODO: should i add a DRAFT status?
        load = Load.objects.create(current_status=Load.Status.DRAFT, **validated_data)
        return load


class LoadListSerializer(serializers.ModelSerializer):
    source = LoadSourceSerializer(read_only=True)
    broker = BrokerSerializer(read_only=True)
    dispatcher = DispatcherUserSerializer(read_only=True)
    driver = LoadDriverSerializer(read_only=True)
    instant_pay = serializers.SerializerMethodField(read_only=True)
    payment_to_date = serializers.SerializerMethodField(read_only=True)
    fees = serializers.SerializerMethodField(read_only=True)
    remain_payment = serializers.SerializerMethodField(read_only=True)

    def get_instant_pay(self, obj):
        try:
            load_settlement = LoadSettlement.objects.get(load=obj)
        except LoadSettlement.DoesNotExist:
            return False
        try:
            load_settlement.invoice.loan
            return True
        except Invoice.loan.RelatedObjectDoesNotExist:
            return False

    def get_payment_to_date(self, obj):
        try:
            load_settlement = LoadSettlement.objects.get(load=obj)
        except LoadSettlement.DoesNotExist:
            return None
        payments = Payment.objects.filter(load_settlement=load_settlement).aggregate(Sum("amount_in_cents"))

        payment_to_date = 0
        if payments.get("amount_in_cents__sum") is not None:
            payment_to_date = round(float(payments.get("amount_in_cents__sum") / 100), 2)
        return payment_to_date

    def get_fees(self, obj):
        try:
            load_settlement = LoadSettlement.objects.get(load=obj)
        except LoadSettlement.DoesNotExist:
            return None
        nauvus_fees_in_cents = load_settlement.nauvus_fees_in_cents
        fee_amount_in_cents = 0
        if self.get_instant_pay(obj):
            fee_amount_in_cents = load_settlement.invoice.loan.fee_amount_in_cents
        nauvus_fees = nauvus_fees_in_cents / 100
        fee_amount = fee_amount_in_cents / 100
        fees = round(float(nauvus_fees + fee_amount), 2)
        return fees

    def get_remain_payment(self, obj):
        try:
            load_settlement = LoadSettlement.objects.get(load=obj)
        except LoadSettlement.DoesNotExist:
            return None
        invoice_amount_due_in_cents = load_settlement.invoice.amount_due_in_cents
        nauvus_fees_in_cents = load_settlement.nauvus_fees_in_cents

        fee_amount_in_cents = 0
        if self.get_instant_pay(obj):
            fee_amount_in_cents = load_settlement.invoice.loan.fee_amount_in_cents

        payments = Payment.objects.filter(load_settlement=load_settlement).aggregate(Sum("amount_in_cents"))

        payment_to_date_in_cents = 0
        if payments.get("amount_in_cents__sum") is not None:
            payment_to_date_in_cents = payments.get("amount_in_cents__sum")

        remain_payment_in_cents = (
            invoice_amount_due_in_cents - payment_to_date_in_cents - (nauvus_fees_in_cents + fee_amount_in_cents)
        )
        remain_payment = round(float(remain_payment_in_cents / 100), 2)
        return remain_payment

    class Meta:
        model = Load
        fields = "__all__"


class DeliveryDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryDocument
        fields = "__all__"


class DeleteDeliveryDocumentSerializer(serializers.Serializer):
    document_id = serializers.UUIDField(required=True)


class CompleteDeliverySerializer(serializers.Serializer):
    delivered_date = serializers.DateTimeField(required=True)


class RateConfirmationDocumentSerializer(serializers.Serializer):
    document = serializers.FileField(required=True, validators=[validate_document_file])
